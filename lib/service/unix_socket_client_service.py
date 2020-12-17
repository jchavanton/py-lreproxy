import queue
import socket
import threading
import os
import time
import subprocess

from logger import logger
from conf.config import Config

module_name = "UnixSocketClientService"


class UnixSocketClientService:
    data_request_queue = queue.Queue()
    sock = None
    active = False
    is_run_unix_o = False
    force_connected = True

    @classmethod
    def run(cls) -> None:

        t = threading.Thread(target=cls.create_unix_file, args=(), daemon=True)
        t.start()
        t.join()
        t = threading.Thread(target=cls.run_user_space, args=(), daemon=True)
        t.start()
        t.join(1)
        threading.Thread(target=cls.worker_check_connection, args=(), daemon=True).start()
        threading.Thread(target=cls.consumer_data_request, args=(), daemon=True).start()

    @classmethod
    def create_unix_file(cls) -> None:

        if os.path.exists(Config.forward_to):
            os.remove(Config.forward_to)

        if not os.path.exists(Config.user_space_c_file_path):
            logger.error("%s not found" % Config.user_space_c_file_path)
        else:
            try:
                if os.path.exists("%s" % Config.user_space_o_file_path):
                    os.remove("%s" % Config.user_space_o_file_path)

                proc = subprocess.Popen(
                    "gcc %s -lm -o %s" % (Config.user_space_c_file_path, Config.user_space_o_file_path),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    universal_newlines=True)
                stdout, stderr = proc.communicate()
                if stdout:
                    logger.debug(stdout)

                if stderr:
                    logger.debug(stderr)
                logger.debug("%s created" % Config.user_space_o_file_path)

            except Exception as e:
                logger.exception("Error: %s" % e)

    @classmethod
    def run_user_space(cls) -> None:

        while True:

            if os.path.exists("%s" % Config.user_space_o_file_path):
                try:

                    if not cls.is_run_unix_o:
                        logger.debug("Starting user_space.o")
                        command = Config.user_space_o_file_path

                        cls.is_run_unix_o = True
                        cls.force_connected = True
                        proc = subprocess.run(command, stdout=subprocess.PIPE, check=True)
                        return_code = proc.returncode
                        logger.debug("CODE: %s" % return_code)
                        if return_code != 0:
                            logger.debug("my code: %s" % return_code)
                            raise subprocess.CalledProcessError(return_code, command)
                        else:
                            logger.debug("Successfully %s running" % Config.user_space_o_file_path)

                        logger.debug("(run_unix_server) end")
                except subprocess.CalledProcessError as e:
                    logger.error("(x) Error : %s" % e)
                    cls.is_run_unix_o = False
                    # cls.sock.close()
                    if os.path.exists(Config.forward_to):
                        os.remove(Config.forward_to)
                    time.sleep(1)
                except OSError as e:
                    logger.error("OS error: %s" % e)
                    cls.sock.close()
                    time.sleep(1)
                except Exception as e:
                    logger.error("Another error: %s", e)
                    cls.sock.close()
                    time.sleep(1)
            else:
                logger.error("%s not found" % Config.user_space_o_file_path)
            time.sleep(5)

    @classmethod
    def worker_check_connection(cls) -> None:
        while True:
            try:
                # cls.is_run_unix_o = True  # TODO removed this is for test
                if cls.is_run_unix_o and cls.force_connected:
                    if os.path.exists(Config.forward_to):
                        cls.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                        cls.sock.connect(Config.forward_to)
                        cls.force_connected = False
                        logger.debug("Successfully socket connected to server")
                    else:
                        logger.error("%s not found" % Config.forward_to)
            except Exception as e:
                logger.debug("Error (worker_check_connection): %s" % e)
                cls.sock.close()
                # logger.debug("Try again for connect socket")
            time.sleep(3)

    @classmethod
    def consumer_data_request(cls) -> None:
        try:
            local_requests = list()
            last_get_time = time.time()
            while True:
                try:
                    req = cls.data_request_queue.get()
                    cls.data_request_queue.task_done()

                    if len(local_requests) == 0:
                        last_get_time = time.time()

                    local_requests.append(req)

                    # if queue is empty,
                    # waiting method for check again
                    if cls.data_request_queue.qsize() == 0:
                        time.sleep(0.1)

                    if time.time() - last_get_time < 1 and cls.data_request_queue.qsize() > 0:
                        continue

                    if cls.data_request_queue.qsize() > 100:
                        logger.warning(
                            'queue data_request_queue have many waited request len:%s'
                            % cls.data_request_queue.qsize())

                    for req in local_requests:
                        cls.data_handler(req)

                    # clear list after send data
                    local_requests = list()

                except queue.Empty as e:
                    logger.debug('data_request_queue is Empty ( %s )' % e)
        except Exception as e:
            logger.error(e)
            time.sleep(3)

    @classmethod
    def data_handler(cls, data: bytes = None) -> None:
        try:
            logger.debug("DATA: UNIX FOR SEND: %s" % data)
            cls.sock.send(data)
            logger.debug("Successfully send data to kernel_space: %s" % data)
        except Exception as e:
            logger.error(e)

    @classmethod
    def execute(cls, cmd: str) -> None:
        popen = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.STDOUT,
                                 universal_newlines=True,
                                 shell=True,
                                 )
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

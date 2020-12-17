import os
import subprocess

from conf.config import Config
from logger import logger


class KernelSpaceModule:

    @classmethod
    def load_kernel_module(cls) -> None:
        if os.path.exists(Config.kernel_space_make_file_path):
            if os.path.exists(Config.kernel_space_c_file_path):
                proc = subprocess.Popen(
                    "cd %s; make -f %s" % (Config.kernel_space_directory, Config.kernel_space_make_file_path),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                stdout, stderr = proc.communicate()
                if stdout:
                    logger.debug(stdout)

                if stderr:
                    logger.error(stderr)

                logger.debug("%s created" % Config.kernel_space_ko_file_path)

                if os.path.exists(Config.kernel_space_ko_file_path):
                    proc = subprocess.Popen("/sbin/rmmod %s" % Config.kernel_space_ko_file_path,
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT
                                            )
                    stdout, stderr = proc.communicate()

                    if stderr and b"Module kernel_space is not currently loaded" in stderr:
                        pass
                    elif stderr and b"Module kernel_space is not currently loaded" not in stderr:
                        logger.error(stderr)

                    if not stderr:
                        logger.debug("rmmod module of kernel space")

                    proxy_config = Config.get_config_ini()
                    if proxy_config:
                        start_port = int(proxy_config.get("start_port", 20000))
                        end_port = int(proxy_config.get("end_port", 30000))
                    else:
                        start_port = 20000
                        end_port = 30000

                    proc = subprocess.Popen(
                        "/sbin/insmod %s min_port=%s max_port=%s" % (Config.kernel_space_ko_file_path, start_port, end_port),
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                    stdout, stderr = proc.communicate()

                    if stdout:
                        logger.debug(stdout)

                    if stderr:
                        logger.error(stderr)
                    logger.debug("insmod module of kernel space")
                else:
                    logger.error("%s not found" % Config.kernel_space_ko_file_path)
            else:
                logger.error("%s not found" % Config.kernel_space_c_file_path)
        else:
            logger.error("%s not found" % Config.kernel_space_make_file_path)

import socket
from struct import pack
import threading

from conf.config import Config
from lib.cache.call_status_request_cache import CallStatusRequest
from lib.service.session_controller_service import SessionControllerService
from logger import logger

module_name = "UDPSocketService"


class UDPSocketService:
    host = Config.socket_udp_host
    port = Config.socket_udp_port
    client_address = None
    sock = None

    @classmethod
    def run(cls) -> None:
        threading.Thread(target=cls.bind_socket, args=(), daemon=True).start()

    @classmethod
    def bind_socket(cls) -> None:

        cls.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cls.sock.bind((cls.host, cls.port))
        logger.debug(f"Socket(UDP) bind on: {cls.host}:{cls.port}")

        while True:
            try:
                data, cls.client_address = cls.sock.recvfrom(1024)
                if data:
                    # logger.debug("Received data on socket: %s" % data)
                    request_id, command = SessionControllerService.get_request_id_and_command(data)
                    # logger.debug("request_id: %s, command: %s" % (request_id, command))
                    CallStatusRequest.set_add_request()
                    if request_id and command:
                        if command == "P":
                            logger.debug(f"Received Command P: {request_id} => {data}")
                            cls.send_pong(request_id, cls.client_address)
                        elif command == "G":
                            logger.debug(f"Received Command G: {request_id} => {data}")
                            cls.send_config(request_id, cls.client_address)
                        elif command == "S":
                            """ 
                            request_id S 
                            src_ip dst_ip s_nat_ip d_nat_ip src_port dst_port s_nat_port d_nat_port timeout call_id 
                            """
                            logger.debug(f"Received Command S: {request_id} => {data}")
                            SessionControllerService.add_request_data_queue.put(data)
                            cls.send_successfully_get_data(data)
                        elif command == "D":
                            pass
                        else:
                            logger.error(f"This command not found in data: {data}")
                    else:
                        logger.error(f"request: {request_id}, command: {command}, data: {data}")

            except Exception as e:
                logger.error("Client Error : %s " % e)

    @classmethod
    def send_pong(cls, req_id: str = None, client_address: str = None) -> None:
        res = bytes("%s P PONG" % req_id, "utf-8")
        cls.sock.sendto(res, client_address)
        logger.debug(f"Sent response to client: {res}")

    @classmethod
    def send_config(cls, req_id: str = None, client_address: str = None) -> None:
        proxy_config = Config.get_config_ini()
        if proxy_config:
            res = bytes("%s G " % req_id, "utf-8") + pack("iii20s20s",
                                                          int(proxy_config.get("start_port")),
                                                          int(proxy_config.get("end_port")),
                                                          int(proxy_config.get("current_port")),
                                                          bytes(proxy_config.get("internal_ip"), "utf-8"),
                                                          bytes(proxy_config.get("external_ip"), "utf-8"))
            cls.sock.sendto(res, client_address)
            logger.debug(f"Sent response to client: {res}")
        else:
            logger.error("Config file is None")

    @classmethod
    def send_successfully_get_data(cls, data: bytes = None) -> None:
        res = bytes("%s%s" % (data.decode("utf-8"), "OK"), "utf-8")
        cls.sock.sendto(res, cls.client_address)
        logger.debug(f"Sent response to client: {res}")

    @classmethod
    def send_successfully_connected_to_unix_o(cls) -> None:
        res = bytes("(UDP) Successfully unix connected ", "utf-8")
        cls.sock.sendto(res, cls.client_address)
        logger.debug(f"Sent response to client: {res}")

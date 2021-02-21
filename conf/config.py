import os
import logging
import configparser


class Config:
    # Config G file
    config_file = "/etc/py_lre_proxy/py_lre_proxy.ini"

    # UDP socket
    socket_udp_host = "127.0.0.1"
    socket_udp_port = 8080

    # Unix socket
    forward_to = "/root/sock"

    # logger
    # log_level = logging.INFO
    log_level = logging.DEBUG
    log_to_file = True
    log_to_console = True
    log_directory = "/var/log/pylreproxy/"
    log_file_name = "pylreproxy.log"

    @classmethod
    def convert_to_logging_format(cls, s: str) -> int:
        s = str(s).lower()
        if s == "critical":
            return logging.CRITICAL
        elif s == "error":
            return logging.ERROR
        elif s == "warning":
            return logging.WARNING
        elif s == "info":
            return logging.INFO
        elif s == "debug":
            return logging.DEBUG
        elif s == "notset":
            return logging.NOTSET
        else:
            return logging.NOTSET

    @classmethod
    def load_ini(cls, file: str = "/etc/py_lre_proxy/py_lre_proxy.ini") -> None:
        if Config.config_file:
            file = Config.config_file
        try:
            if os.path.exists(file):
                variables = [i for i in dir(cls) if not callable(i) and not i.startswith("_")]
                cfg = configparser.ConfigParser()
                cfg.read(file)
                for section in cfg.sections():
                    for a, b in cfg.items(section):
                        if a in variables:
                            attr = getattr(cls, a)
                            if a == "log_level":
                                b = cls.convert_to_logging_format(b)
                            elif str(b).lower() == 'none':
                                b = None
                            elif isinstance(attr, str):
                                pass
                            elif isinstance(attr, bool):
                                # isinstance(attr, bool) and isinstance(attr, int) have conflict
                                # So check bool first to avoid inconsistency
                                if str(b).lower() == "true":
                                    b = True
                                elif str(b).lower() == "false":
                                    b = False
                                else:
                                    # logger.error('Incorrect data type in config. Variable "%s" '
                                    #              'should be boolean (True/False).' % a)
                                    pass
                            elif isinstance(attr, int):
                                if not str(b).isdigit():
                                    # logger.error('Incorrect data type in config. Variable "%s" should be integer.' % a)
                                    continue
                                b = int(b)
                            elif isinstance(attr, float):
                                try:
                                    b = float(b)
                                except ValueError as eee:
                                    # logger.error('Incorrect data type in config. Variable "%s" should be float.' % a)
                                    continue
                            elif isinstance(attr, list):
                                b = str(b).split(',') if len(str(b)) > 0 else list()
                            elif isinstance(attr, tuple):
                                b = tuple(str(b).split(',')) if len(str(b)) > 0 else tuple()
                            setattr(cls, a, b)
            else:
                # logger.debug("config file not found")
                pass
        except Exception as e:
            from logger import logger
            logger.error("unable to load %s, reason: %s" % (file, e))

    @classmethod
    def get_config_ini(cls, file: str = "/etc/lre_proxy/config_py_lre_proxy.ini") -> dict:
        try:
            if Config.config_file:
                file = Config.config_file

            config = configparser.ConfigParser()
            if os.path.exists(file):
                config.read(file)
                return {k: v for k, v in config.items("DEFAULT")}
            else:
                logging.error("config_lre_proxy file %s not found" % file)
        except Exception as e:
            logging.error(e)

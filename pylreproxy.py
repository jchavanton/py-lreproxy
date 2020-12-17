import signal
import sys
import time
from concurrent.futures.thread import ThreadPoolExecutor

from conf.config import Config
from lib.shell.kernel_space_module import KernelSpaceModule

Config.load_ini()
import glob
import os
import _version
from logger import logger

modules = {}


def load_modules():
    d = os.path.dirname(os.path.realpath(__file__))
    print(d)
    m1 = glob.glob(os.path.join(d, "lib/service/*.py"))
    module_files = m1
    # print(module_files)
    for m in module_files:
        if m.__contains__("__init__.py"):
            continue
        m = m.replace(d, "").replace(os.sep, ".").replace(".py", "")
        m = m[1:]
        _, __, mm = str(m).rpartition('.')
        try:
            p = __import__(m, fromlist=['module_name'])
            module_name = str(getattr(p, 'module_name'))
            h = getattr(p, module_name)
            modules[module_name] = h
        except Exception as e:
            logger.error('Error while loading module %s: message: %s' % (mm, e))


load_modules()


class Server:
    executor = ThreadPoolExecutor(max_workers=100)

    @staticmethod
    def run():
        for a, m in modules.items():
            if m is not None:
                future = Server.executor.submit(m.run)
                logger.debug("Loading service %s: done" % a)
            else:
                logger.error("Loading service %s: failed" % a)


def signal_handler(signal, frame):
    logger.debug('Signal SIGINT')
    if os.path.exists(Config.forward_to):
        os.remove(Config.forward_to)
    sys.exit(0)


def auto_create_config_file():
    if not os.path.exists(Config.config_file):
        context = b'[DEFAULT]\nstart_port : 20000\nend_port : 30000\ncurrent_port : 20000\n' \
                  b'internal_ip : 192.168.10.226\nexternal_ip : 192.168.10.226\n'
        directory = os.path.dirname(Config.config_file)
        os.makedirs(directory)
        with open(Config.config_file, "w") as f:
            f.write(context.decode("utf8"))
            logger.debug("Auto create config file to: %s" % Config.config_file)


if __name__ == "__main__":
    logger.info("Version: %s" % _version.__version__)
    logger.info("Starting lre_proxy")
    signal.signal(signal.SIGINT, signal_handler)
    auto_create_config_file()
    KernelSpaceModule.load_kernel_module()
    Server.run()

    while True:
        logger.debug("First While ...")
        time.sleep(1000)

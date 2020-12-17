import os
import threading
import time

import psutil

from lib.cache.call_status_request_cache import CallStatusRequest
from logger import logger

module_name = "MonitoringService"


class MonitoringService:

    @classmethod
    def run(cls) -> None:
        threading.Thread(target=cls.worker_monitor, args=(), daemon=True).start()
        threading.Thread(target=cls.worker_temporary, args=(), daemon=True).start()

    @classmethod
    def worker_monitor(cls) -> None:

        while True:
            try:
                logger.debug("Monitoring Service: %s" % CallStatusRequest.get_all())
                logger.debug("Active count threading is running : %s\n\n\n" % threading.active_count())
                time.sleep(10)
            except Exception as e:
                logger.error(e)
                time.sleep(15)

    @classmethod
    def worker_temporary(cls) -> None:
        try:
            while True:
                process = psutil.Process(os.getpid())
                logger.debug("Cpu Percent: %s Memory RSS: %s Memory VMS:: %s Threads:%s  Full info Memory: %s" %
                             (process.cpu_percent(), cls.convert_size(process.memory_info().rss),
                              cls.convert_size(process.memory_info().vms),
                              threading.active_count(), process.memory_full_info()))
                logger.debug("Ram used percentage: %s " % cls.get_data_ram())
                logger.debug("Cpu used percentage: %s " % cls.get_data_cpu())
                time.sleep(30)
        except Exception as e:
            logger.error(e)
            time.sleep(30)

    @classmethod
    def get_data_ram(cls) -> int:
        try:
            total = psutil.virtual_memory().total
            used = psutil.virtual_memory().used
            percent = round(used / total * 100, 1)

            return percent
        except Exception as e:
            logger.error(e)
            return 0

    @classmethod
    def get_data_cpu(cls) -> int:
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(e)
            return 0

    @classmethod
    def convert_size(cls, size_bytes: int) -> str:
        # todo temporary function
        import math

        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

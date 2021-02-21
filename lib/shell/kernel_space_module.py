import os
import subprocess

from conf.config import Config
from lib.tools.common_functions import get_lreproxy_module_directory, get_lreproxy_module_make_file_path, \
    get_lreproxy_module_c_file_path, get_lreproxy_module_ko_file_path
from logger import logger


class KernelSpaceModule:

    @classmethod
    def load_kernel_module(cls) -> None:
        if os.path.exists(get_lreproxy_module_make_file_path()):
            if os.path.exists(get_lreproxy_module_c_file_path()):
                proc = subprocess.Popen(
                    f"cd {get_lreproxy_module_directory()}; make -f {get_lreproxy_module_make_file_path()}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                stdout, stderr = proc.communicate()
                if stdout:
                    logger.debug(stdout)

                if stderr:
                    logger.error(stderr)

                logger.debug(f"{get_lreproxy_module_ko_file_path()} created")

                if os.path.exists(get_lreproxy_module_ko_file_path()):
                    proc = subprocess.Popen(f"/sbin/rmmod {get_lreproxy_module_ko_file_path()}",
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
                        f"/sbin/insmod {get_lreproxy_module_ko_file_path()} min_port={start_port} max_port={end_port}",
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
                    logger.error(f"{get_lreproxy_module_ko_file_path()} not found")
            else:
                logger.error(f"{get_lreproxy_module_c_file_path()} not found")
        else:
            logger.error(f"{get_lreproxy_module_make_file_path()} not found")

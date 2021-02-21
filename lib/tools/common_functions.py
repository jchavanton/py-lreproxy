import os
from pathlib import Path


def get_root_project_directory() -> str:
    return str(Path(__file__).parent.parent.parent)


def get_user_space_c_file_path() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "user_space.o", "user_space.c")


def get_user_space_o_file_path() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "user_space.o", "user_space.o")


def get_lreproxy_module_directory() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "kernel_space.ko")


def get_lreproxy_module_make_file_path() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "kernel_space.ko", "Makefile")


def get_lreproxy_module_c_file_path() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "kernel_space.ko", "lreproxy_module.c")


def get_lreproxy_module_ko_file_path() -> str:
    return os.path.join(get_root_project_directory(), "lib", "c", "kernel_space.ko", "lreproxy_module.ko")

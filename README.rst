py-lreproxy - Python Lre Proxy
=============================================

Installation
------------

You should downloaded the source package locally and run with command:

    Extract project::

        tar -xvf py-lreproxy-master.tar.gz -C /usr/src/
        mv /usr/src/py-lreproxy-master /usr/src/py-lreproxy

    Install psutil::

        apt update
        apt install python3-pip
        pip3 install psutil

    Install linux headers::

        uname -r
        apt install linux-headers-$(uname -r)

    Run project with command::

        python3 /usr/src/py-lreproxy/pylreproxy.py



Dependencies
------------
Py-lreproxy supports *Python3.6+* and test on *"Debian GNU/Linux 10 (buster)"*


Structure code
--------------
In this project, requests are sent to pylreproxy from Kamailio on the UDP socket and then sent to the kernel space via user space.

Each request contains the following commands:

- P (PING):
    `` *request_id P* ``

        By sending this request from Kamailio, he sends pylreproxy in response to **PONG** to inform Kamailio that the was ready.

- G (CONFIG):
    `` *request_id G* ``

        By sending this request from Kamailio, he sends pylreproxy in response to this information **"start_port, end_port, current_port, internal_ip and external_ip"**
        The config file is in the following path: **"/etc/py_lre_proxy/py_lre_proxy.ini"**

- S (DATA):
    `` *request_id S src_ip dst_ip s_nat_ip d_nat_ip src_port dst_port s_nat_port d_nat_port timeout call_id* ``

        By sending this request from Kamailio to pylreproxy, the data is sent to the kernel space


Config files:
-------------
The config file is in **/etc/py_lre_proxy/py_lre_proxy.ini** path.

Default config::

    [DEFAULT]
    start_port : 20000
    end_port : 30000
    current_port : 20000
    internal_ip : 192.168.10.226
    external_ip : 192.168.10.226

    config_file: /etc/py_lre_proxy/py_lre_proxy.ini

    socket_udp_host : "127.0.0.1"
    socket_udp_port : 8080

    forward_to : "/root/sock"

    og_level : logging.DEBUG
    log_to_file : True
    log_to_console : True
    log_directory : "/var/log/pylreproxy/"
    log_file_name : "pylreproxy.log"



Log files
----------
Use the following command to check lreproxy_module logs::

    dmesg -hs


Use the following command to check user_space and pylreproxy logs::

    tail -n 1000 -f /var/log/pylreproxy/pylreproxy.log

    tail -n 1000 -f /var/log/pylreproxy/user_space.log


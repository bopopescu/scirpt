#!/usr/bin/python2.7
from main import (time,HostHandler,ServiceHandler)

host_test = ServiceHandler()
host = 'localhost'
re_hostname = 'compute-02'
#re_ip = '10.2.0.21'
group_name = "zhang"
service_name = "ipmi"

n = host_test._file_cp(re_hostname,service_name)
print n

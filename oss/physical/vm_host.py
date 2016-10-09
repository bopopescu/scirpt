#!/usr/bin/python2.7

from db import DB
import datetime


time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class VmHandler():
    def __init__(self):
        self.db = DB("root","password","localhost","falcon_portal")
        self.tab_host = "host"
        self.tab_vm = "vm_host"
        self.interval = 300

    def vm_host_add(self, hostname, ip, uuid, node, interval=self.interval):
        #Inserting  into table host for alerting
        try:
            self.db._insert_(self.tab_host,'(hostname,ip)',hostname,ip)
            self.db._insert_(self.tab_vm,'(hostname,float_ip,uuid,node,state,interval,create_time,update_time)',hostname,ip,uuid,node,1,interval,time,time)
        except Exception,e:
            print str(e)
            return False
        return True
    def vm_host_del(self, uuid):
        try:
            self.db._update_(self.tab_vm, "state=0",'where uuid="%s"' % uuid)
        except Exception,e:
            print str(e)
            return False
        return True
    def update_interval(self, uuid, interval):
        try:
            self.db._update_(self.tab_vm,'interval=%d' % interval,'where uuid="%s"' % uuid)
        except Exception,e:
            print str(e)
            return False
        return True




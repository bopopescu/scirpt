#!/usr/bin/python2.7
import paramiko
from db import DB
import MySQLdb
import time
import config

username = config.user_compute
password = config.passwd_compute
remote_file = "/tmp/temp-instances"
file_list = config.compute_node

def sync_file_handler(ip_addr,local_file,remote_file):
    t = paramiko.Transport(ip_addr)
    t.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remote_file, local_file)
    t.close()

def sync_data():
    data_list = []
    for i in file_list:
        try:
            local_file = i+"-instances.txt"
            sync_file_handler(i, local_file, remote_file)
        except Exception,e:
            print str(e)
            continue
        with open(local_file) as f:
            for line in f.readlines():
                data_list.extend(line.split())
    return data_list

class SqlHandler(DB):
    def __init__(self):
        self.user = conf.db_user
        self.password = conf.db_passwd
        self.host = conf.db_host
        self.dbname = "falcon_portal"
        self.tabname = "host"
        self.grpname = "grp"
        self.relname = "grp_host"
        self.conn = MySQLdb.connect(user=self.user, passwd=self.password,
                                    host=self.host, db=self.dbname)
        self.cursor = self.conn.cursor()
    def select_vm(self):
        data_list = self._select_many_(self.tabname, "hostname,id",'where hostname like "instance%"')
        return data_list
    def insert_vms(self,list_vms):
        tab_para = "(hostname,ip,agent_version,plugin_version,maintain_begin,maintain_end)"
        for vm in list_vms:
            try:
                self._insert_(self.tabname, tab_para, vm,"192.168.1.1","5.0","128",0,0)
            except Exception,e:
                print str(e)
                return None
        return True

    def delete_vms(self,list_vms):
        for  i in list_vms:
            try:
                host_id = self._select_(self.tabname,"id",'where hostname="%s"' % i)["id"]
                self._del_(self.relname,'where host_id=%d' % int(host_id))
                self._del_(self.tabname, 'where hostname="%s"' % i)
            except Exception,e:
                print str(e)
                return None
        return True
    def insert_vm_group(self,list_vms,grp_name):
        grp_id =  self._select_(self.grpname,"id",'where grp_name="%s"' % grp_name)["id"]
        for i in list_vms:
            try:
                host_id = self._select_(self.tabname,"id",'where hostname="%s"' % i)["id"]
                self._insert_(self.relname,"(grp_id,host_id)",grp_id,host_id)
            except Exception,e:
                print str(e)
                return None
        return True
    def update_vms(self,list_vms,grp_name):
        if self.insert_vms(list_vms):
            if self.insert_vm_group(list_vms,grp_name):
                return True
        return None


def compare_instances():
    grp_name = "vms_group"
    t_b = time.time()
    vms_list = sync_data()
    t_e = time.time()
    print "sync vm from compute node time is %f" % (t_e-t_b)

    handler = SqlHandler()
    t_b = time.time()
    db_hosts_handler = handler.select_vm()
    t_e = time.time()
    print "check vm from db time is %f" % (t_e-t_b)


    if not db_hosts_handler:
        db_hosts_list = []
    else:
        db_hosts_list = [i["hostname"] for i in db_hosts_handler]

        ## vm have and db not have;then insert vm into db
    insert_list = list(set(vms_list).difference(set(db_hosts_list)))
    if insert_list:
        t_b = time.time()
        handler.update_vms(insert_list,grp_name)
        t_e = time.time()
        print "insert vm into db time is %f" % (t_e-t_b)

    ## vm have not and db have;then delete vm from db
    del_list = list(set(db_hosts_list).difference(set(vms_list)))
    if del_list:
        t_b = time.time()
        handler.delete_vms(del_list)
        t_e = time.time()
        print "delete vm from db time is %f" % (t_e-t_b)
    return "success"




if __name__ == '__main__':
    t_b = time.time()
    flag = compare_instances()
    t_e = time.time()
    t_duration = t_e - t_b
    print "total time is %f" % t_duration

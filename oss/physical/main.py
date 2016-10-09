#!/usr/bin/python
#author:sean-zhang
#date 2015-09-15
#func: provide physcial machine monitor interface function for oss
import  salt.client as Client
import requests
import os
import datetime
import re
from db import DB

time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class HostHandler():
    """ func: modified host
        para: ips -- 'compute-*'
        methods:  agent_restart     --restart agent
                  add_host          --  enable true , agent transfer data to transfer
                  del_host          --  disable true
                  view_host         -- view agent status
    """
    def __init__(self):
        self.client = Client.LocalClient()
        self.file_path = '/home/work/open-falcon/agent/control'
        self.file_cfg = '/home/work/open-falcon/agent/cfg.json'
        self.enable_s = '"enabled": true'
        self.disable_s = '"enabled": false'
        self.path_file = "/home/work/open-falcon/agent"
        self.ant_cfg = "/home/work/open-falcon/anteye/cfg.json"
        self.ant_file = "/home/work/open-falcon/anteye/control"
        self.db=DB("root","password","localhost","falcon_portal")
        self.tab_host = "falcon_hosts"
        self.tab_service = "falcon_service"

# restart agent
    def _agent_restart(self,ips):
        cmd = self.file_path+' restart'
        exr = self.judge_ipstype(ips)
        n = self.client.cmd(ips,'cmd.run',[cmd],exr_form=exr)
        return n

    def _agent_status(self,ips):
        cmd = self.file_path+' status'
        exr = self.judge_ipstype(ips)
        n = self.client.cmd(ips,'cmd.run',[cmd],exr_form=exr)
        return n
#judge which type of ips
    def judge_ipstype(self,ips):
        if type(ips) == 'list' or 'tuple':
            ips = ','.join(ips)
            return ("list",ips)
        elif '*' in ips:
            return "pcre"
        else:
            return "glob"
# judge agent exist
    def _agent_exist(self, ips):
        exr = self.judge_ipstype(ips)
        rep = self.client.cmd(ips, "file.directory_exists", [self.path_file],exr_form=exr)
        return rep[ips]

#put agent 
    def _agent_put(self, ips):
        exr = self.judge_ipstype(ips)
        self.client.cmd(ips, "file.makedirs",['/home/work/open-falcon'])
        rep = self.client.cmd(ips, "cp.get_dir", ["salt://file/open-falcon/agent","/home/work/open-falcon/"])
        self.client.cmd(ips,'file.set_mode',['/home/work/open-falcon/agent/control','755'])
        self.client.cmd(ips,'file.set_mode',['/home/work/open-falcon/agent/falcon-agent','755'])
        return rep

#agent stop
    def _agent_stop(self, ips):
        cmd = self.file_path+' stop'
        exr = self.judge_ipstype(ips)
        n = self.client.cmd(ips,'cmd.run',[cmd],exr_form=exr)
        return n
#modify ant
    def _ant_hander(self, ip):
        url_data = '"agent,http://%s:1988/health"' % ip
        content = []
        expr = re.compile('/health"$')
        with open(self.ant_cfg) as f:
            for line in f.readlines():
                content.append(line)
                if url_data in line:
                    f.close()
                    print "Anety:%s already in %s" % (url_data, self.ant_cfg)
                    return True
                elif expr.search(line.strip()):
                    content[-1] = content[-1].strip()+',\n'
                    content.append("%s\n" % url_data)
                
        f.close()
        with open(self.ant_cfg,"w") as f:
            f.writelines(content)
        f.close()
        cmd = self.ant_file + ' restart'
        os.system(cmd) 
        return True

    def _ant_del(self, ip):
        url_data = '"agent,http://%s:1988/health"' % ip
        data_list = []
        f = open(self.ant_cfg)
        for line in f.readlines():
            if not re.search(url_data,line):
                data_list.append(line)
        f.close()
        data_list[-4] = data_list[-4].strip().strip(',')+'\n'
        f = open(self.ant_cfg, "w")
        f.writelines(data_list)

    def add_host(self, ips, hostname):
        import pdb
        temp_name = re.search("(?P<type>\w+)-(?:\d*)",hostname)
        para_name = "(hostname,ip,type,state,update_time,create_time)"
	if temp_name:
	    Type = temp_name.group('type')
	else:
	    Type = "null"
        if not self._agent_exist(hostname):
            self._agent_put(hostname)
        #pdb.set_trace()
        if not  self.db._select_(self.tab_host, 'hostname', 'where hostname="%s"' % hostname):
            self.db._insert_(self.tab_host,para_name,hostname,ips,Type,"init",time,time)
        self._agent_restart(hostname)
        if  self._agent_status(hostname)[hostname] == 'stop':
            print "Err!agent can`t start,Please check immediatry"
            exit(1)
        self._ant_hander(ips)
        self.db._update_(self.tab_host,'state="start"','where hostname="%s"' % hostname)
        n = self.db._select_(self.tab_host,'hostname,ip,type,state','where hostname="%s"' % hostname)
        return n
    
    def del_host(self, ips, hostname):
        self._ant_del(ips)
        self._agent_stop(hostname)
        self.db._update_(self.tab_host,'state="stop"', 'where hostname="%s"' % hostname)
        n = self.db._select_(self.tab_host,'hostname,ip,type,state','where hostname="%s"' % hostname)
        return n

    def sele_host(self,ips,hostname):
        n = self.db._select_(self.tab_host,'hostname,ip,type,state','where hostname="%s"' % hostname)
        return n
    def end_host(self):
        self.db._close_()




 


class ServiceHandler():
#auth user   and login
    def __init__(self):
        self.user = 'root'
        self.password = '123456'
        self.base_url = "http://10.1.0.12:5050"
        self.auth_url = "http://10.1.0.12:1234/auth/login"
        self.base_path = "/home/work/open-falcon/agent/plugin"
        self.salt_base = "salt://file/open-falcon/plugin/compute"
        data = {"name":self.user,"password":self.password}
        self.s = requests.session()
        self.s.post(self.auth_url,data=data)
        self.client = Client.LocalClient()
        self.db=DB("root","password","localhost","falcon_portal")
        self.tab_service = "falcon_service"
    
    def _bind_service(self,group_name,service_name):
        url = self.base_url + "/plugin/bind"
        group_id = self._get_id(group_name)
        data = {"group_id":group_id,"plugin_dir":service_name}
        rep = self.s.post(url, data=data)
        return rep
    def _unbind_service(self,group_name,service_name):
        group_id = self._get_id(group_name)
        plugin_id = self.db._select_("plugin_dir",'id','where grp_id=%d and dir="%s"' % (group_id,service_bane))
        url = self.base_url + "/plugin/delete/%d" % plugin_id
        rep = self.s.get(url)
        return  rep
    def _plugin_check(self, group_name, service_name):
        group_id = self._get_id(group_name)
        result = self.db._select_(self.tab_serivce,'id','where grp_id=%d and dir="%s"' % (group_id,service_bane))
        return result
#    def _add_job(self, hostname, service_name):
#        Path = os.path.join(self.base_path,service_name+'/main.py')
#        rep = self.client.cmd(hostname, "cron.set_job", ['root','python %s' % Path, '*/1','*','*','*','*'])
#       return rep

#    def _del_job(self, hostname, service_name):
#        Path = os.path.join(self.base_path,service_name+'/main.py')
#        rep = self.client.cmd(hostname, "rm_job", ['root','python %s' % Path])
#        return rep

    def  _file_exist(self, hostname, service_name):
        Path = os.path.join(self.base_path,service_name)
        rep = self.client.cmd(hostname, "file.directory_exists", [Path])
        return rep[hostname]

    def _file_remove(self, hostname, service_name):
        Path = os.path.join(self.base_path,service_name)
        if self._file_exist(hostname, service_name):
            rep = self.client.cmd(hostname, "file.remove", [Path])
            return rep
            
    
    def _file_cp(self, hostname, service_name):
        Path = self.base_path
        service_path = os.path.join(Path,service_name)
        salt_path = os.path.join(self.salt_base,service_name)
        if not self._file_exist(hostname, service_name):
            self.client.cmd(hostname, "cp.get_dir", [salt_path,Path])
            self.client.cmd(hostname,"file.set_mode",[os.path.join(service_path,'*'),'755'])
            
            
    def _get_id(self, grpname):
        id = self.db._select(self.tab_service, "id", 'where grp_name="%s"' % grpname)
        return id

    def add_service(self, hostname, service_name, group_name):
        if not self.db._select_(self.tab_service,"id",'where hostname="%s" and service_name="%s"' % (hostname, service_name)):
            self.db._insert_(self.tab_service, "(service_name,hostname,state,update_time,create_time)",service_name,hostname,"init",time,time)
        self._file_cp(hostname, service_name)
        if not _plugin_check(group_name, service_name):
            self._bind_service(group_name, service_name)
        self.db._update_(self.tab_service,'state="start"','where hostname="%s" and service_name="%s"' % (hostname,service_name))
        return True

    def del_service(self, hostname, service_name, group_name):
        self._unbind_service(group_name,service_name)
        self.db._update_(self.tab_host,'state="stop"','where hostname="%s" and service_name="%s"' % (hostname,service_name))
        return True

    def sel_service(self, hostname, service_name):
        self.db._select_(self.tab_service, "service_name,hostname,state", 'where hostname="%s" and service_name="%s"' % (hostname,service_name))
    
    def end_service(self):
        self.db._close_()



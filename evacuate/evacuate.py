#!/usr/bin/python2.7
import MySQLdb
import json
import flask
import re
import subprocess
import requests
import pdb

"""
 function:   provide data for openstack developer with rest interface
	REST INSERFACE:	http://10.1.0.12:6080/data
	return data with dict type
"""

class Evacuate():
## conn db
    def __init__(self,user,password,host,dbname):
        self.query_url = "http://127.0.0.1"
        self.user = user
        self.password = password
        self.host = host
        self.dbname = dbname
        self.login = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.dbname)
        self.cursor = self.login.cursor()
## get data from db
    def query_data(self,table_name):
        select_list = ['controller*','compute*','storage*']
        data_list = []
        sql = "select hostname,ip from %s" % table_name
        n = self.cursor.execute(sql)
        all = self.cursor.fetchall()
        for i in all:
            for j in select_list:
                if re.match(j,i[0]):
                    list_i = list(i)
                    list_i.append(j.strip('*'))
                    data_list.append(list_i)
                    break
        return data_list   #### return [[hostname,ip,type],[...]...]

## get instance from table vm_hosts
    def query_instances(self,node):
	data_list = []
        sql = 'select hostname,uuid from vm_host where node = "%s"' % node
        try:
            n = self.cursor.execute(sql)
            result = self.cursor.fetchall()
	    for i in result:
	        data_dict = {}
		data_dict["name"] = i[0]
		data_dict["uuid"] = i[1]
            	data_list.append(data_dict)
        except Exception,e:
            print  str(e)
            return []
## return list

        return data_list

    def update_instances(self,instance,node):
        sql = 'update vm_host set node="%s" where hostname="%s"' % (node,instance)
        try:
            n = self.cursor.execute(sql)
        except Exception,e:
            print str(e)
            self.login.rollback()
            return None
        self.login.commit()
        return True



        
### check the host is living through pinging
    def host_alive(self,ipaddress):
        cmd = "ping -c1 -W1 %s > /dev/null" % ipaddress
        if subprocess.call(cmd,shell=True) == 0:
            return "alive"
        else:
            return "down"
### check the service is living through open-falcon last interface
    def compute_service_alive(self, host, item):
        url = self.query_url+ ':9966/graph/last'
#    header = {'Content-Type':'application/json-rpc'}
        data_dict = {}
        data_dict['endpoint'] = host
        data_dict['counter'] = item
        data = json.dumps([data_dict])
        try:
            response = requests.post(url,data=data)
            value =  json.loads(response.text)[0]['value']['value']
	except Exception:
	    return "down"
        if int(value) == 1:
            return "running"
        else:
            return "down"
    def agent_alive(self, compute_ip):
        url = "http://" + compute_ip + ":1988/health"
        try:
            rep = requests.get(url)
        except Exception,e:
            print str(e)
            return "down"
        if rep.text == 'ok':
            return "alive"
        return "down"


app = flask.Flask(__name__)
########## funcion data interface
@app.route('/data')
def compute_monitor():
    data_list = []
#    item = 'nova.pro.nova_compute'
    item = 'nova.pro.nova-compute/function=nova,module=service'
    user = 'falcon'
    password = 'password'
    host = 'localhost'
    dbname = 'falcon_portal'
    tablename = 'host'
    getdata =  Evacuate(user,password,host,dbname)
    all_data = getdata.query_data(tablename)
    for i in all_data:
        data_dict = {}
        hostname = i[0]
        ip = i[1]
        type = i[2]
        host_flag = getdata.host_alive(ip)
        if type == 'compute' and host_flag == 'alive':
            service_flag = getdata.compute_service_alive(hostname,item)
            agent_flag = getdata.agent_alive(ip)
            data_dict['service_status'] = service_flag
            data_dict['agent_status'] = agent_flag
            data_dict['instances'] = getdata.query_instances(hostname)
        data_dict['ip'] = ip
        data_dict['hostname'] = hostname
        data_dict['node'] = type
        data_dict['physical_status'] = host_flag
        data_list.append(data_dict)
    return json.dumps(data_list)

@app.route("/update-vm",methods=['POST'])
def update_vm_hosts():
    user = 'falcon'
    password = 'password'
    host = 'localhost'
    dbname = 'falcon_portal'
    tablename = 'host'
    getdata =  Evacuate(user,password,host,dbname)
    computes = json.loads(flask.request.data)
    if not computes:
        print "receive no data"
        return "no data",500
    print computes
    for handler in computes:
        for node in handler:
            instances = handler[node]
            if not instances:
                print "return %s have no instance" % node
                continue
            for instance in instances:
                if not getdata.update_instances(instance, node):
                    print "update %s to %s handler fail" % (instance,node)
                    continue
    return flask.jsonify(msg="success"),200

############# test
@app.route('/health')
def test():
    return "ok"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=6080,debug=True)


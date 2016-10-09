#!/usr/bin/python2.7
import time,datetime
import json
import requests
from multiprocessing import Process
from db import  DB
import config

from flask import jsonify,Flask
from logger import Logger
import os


dirname = os.path.dirname(os.path.abspath(__file__))
log = Logger(debug=True,filename=os.path.join(dirname,"app.log"))


### create or update db
class SQLHandler():
	def __init__(self):
		self.dbs = DB(config.mysqldb_user, config.mysqldb_password,config.mysqldb_host,config.mysqldb_db)
		self.vm_table = config.t_vm
		self.host_table = "host"
	def update_db(self,*args, **kwargs):
		time  =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		tab_para = "(hostname,uuid,node,state,interval_time,update_time,create_time)"
		params = 'where hostname = "%s"' % kwargs['hostname']
		try:
			if  not self.dbs._select_(self.vm_table ,'hostname',params):
				self.dbs._insert_(self.vm_table, tab_para,kwargs['hostname'],kwargs["uuid"]
					,kwargs['node'],kwargs['state'],kwargs['interval_time'],time,time)
			else:
### exchange tab_value type
				data_list = []
				for key in args:
					value = kwargs[key]
					expr = '%s="%s"' % (key,value)
					print expr
					data_list.append(expr)
				tab_value = ','.join(data_list)
				print tab_value
				self.dbs._update_(self.vm_table, tab_value, params)
		except Exception,e:
			print str(e)
			return None
		return True

	def del_db(self, hostname):
		tab_para = 'where hostname = "%s"' % hostname
		try:
			self.dbs._del_(self.vm_table, tab_para)
		except Exception,e:
			print str(e)
			return None
		return True

	def  select_db(self):
		type_list = []
		result_dict = {}
	# get node type
		for i in self.dbs._select_many_(self.vm_table, "node", "group by node"):
			type_list.append(i['node'])
		for node in type_list:
			data_dict = {}
			try:
				data_list_60 = [k['hostname'] for  k in self.dbs._select_many_(self.vm_table, "hostname",'where node="%s" and interval_time=%d' % (node,60))]
			except Exception:
				data_list_60 = None
			try:
				data_list_300 = [k['hostname'] for k in self.dbs._select_many_(self.vm_table, "hostname",'where node="%s" and interval_time=%d' % (node,300))]
			except Exception:
				data_list_300 = None
			data_dict['60'] = data_list_60
			data_dict['300'] = data_list_300
			result_dict[node] = data_dict
		return result_dict

	def select_db_60(self):
		data_dict = {}
		data_handler = self.dbs._select_many_(self.vm_table,"node,hostname","where interval_time=60")
		if not data_handler:
			return None
		for i in data_handler:
			node = i["node"]
			instance = i["hostname"]
			if node in data_dict:
				data_dict[node].append(instance)
			else:
				data_dict[node] = [instance]
		return data_dict

	def select_db_300(self):
		data_dict = {}
		data_handler = self.dbs._select_many_(self.vm_table,"node,hostname","where interval_time=300")
		if not data_handler:
			return None
		for i in data_handler:
			node = i["node"]
			instance = i["hostname"]
			if node in data_dict:
				data_dict[node].append(instance)
			else:
				data_dict[node] = [instance]
		return data_dict


	def create_host(self,hostname,ip):
		time  =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		try:
			if  self.get_host(hostname):
				log.debug("%s already exist in table host" % hostname)
				return None
			self.dbs._insert_(self.host_table, "(hostname,ip,agent_version,plugin_version,maintain_begin,maintain_end,update_at)",hostname, ip,"5.0","128",0,0,time)
		except Exception,e:
			log.error(str(e))
			return None
		return True
	def delete_host(self,hostname):
		time  =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		params = 'where hostname="%s"' % hostname
		try:
			if not self.get_host(hostname):
				log.debug("%s not exsit in table host" % hostname)
				return None
			self.dbs._del_(self.host_table,params)
		except Exception,e:
			log.error(str(e))
			return None
		return True
	def get_host(self,hostname):
		params = 'where hostname="%s"' % hostname
		try:
			rep = self.dbs._select_(self.host_table, "id,hostname",params)["id"]
		except Exception,e:
			log.error(str(e))
			return None
		return rep
        

	def get_host_name_where_id(self, host_id):
 	        params = params = 'where id="%s"' % host_id

                try:
                        rep = self.dbs._select_(self.host_table, "id,hostname",params)["hostname"]
                        log.debug("------------%s" %rep)
                except Exception,e:
                        log.error(str(e))
                        return None
                return rep



#################### send data with interval
def send_data(interval):
	while True:
		handler = SQLHandler()
		if int(interval) == 60:
			data_dict = handler.select_db_60()
			print 20*"#"
			print "60-data_dict:",data_dict
			print 20*"#"
			if not data_dict:
				print "interval 60 have no data,wait...."
				time.sleep(60)
				continue
		elif int(interval) == 300:
			data_dict = handler.select_db_300()
			print 20*"#"
			print "300-data_dict:",data_dict
			print 20*"#"
			if not data_dict:
				print "interval 300 have no data,wait...."
				time.sleep(60)
				continue
		for node in data_dict:
			instance_list = data_dict[node]
	### need concurrence??
	## need process pool
			p_name = "p_"+node
			p_name = Process(target=inform_compute,args=([node,instance_list]))
			p_name.start()
			p_name.join(0.00001)
		time.sleep(interval)

######################## main
def main():
	p60 = Process(target=send_data,args=([60]))
	p300 = Process(target=send_data,args=([300]))
	p60.start()
	p300.start()
	p60.join()
	p300.join()


#### inform computeL
def inform_compute(node,instances_list):
	url = "http://%s:9193/vm_monitor/" % node
	data = {'instances_list': instances_list}
	rep = requests.post(url,data=json.dumps(data))
	if  rep.status_code != 200:
		print "send instances to %s fail!" % node
		return  None
	print "send %s success to %s" % (json.dumps(instances_list),node)
	return True


if __name__ == '__main__':

	main()


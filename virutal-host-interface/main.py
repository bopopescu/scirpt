#!/usr/bin/python2.7
from  flask import Flask,request,jsonify
import time,datetime
import json
import requests
from multiprocessing import Process
from db import  DB
from config import *

app =  Flask(__name__)
### create or update db
def update_db(*args, **kwargs):
	db = DB(mysqldb_user, mysqldb_password,mysqldb_host,mysqldb_db)
	tabname = t_vm
	time  =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	tab_para = "(hostname,node,state,interval_time,update_time,create_time)"
	params = 'where hostname = "%s"' % kwargs['hostname']
	try:
		if  not db._select_(tabname,'hostname',params):
			db._insert_(tabname, tab_para,kwargs['hostname'],
				kwargs['node'],kwargs['state'],kwargs['interval_time'],time,time)
		else:
### exchange tab_value type
			data_list = []
			for key in args:
				value = kwargs[key]
				expr = "%s=%s" % (key,value)
				data_list.append(expr)
			

                        tab_value = ','.join(data_list)
                        print tab_value
			db._update_(tabname, tab_value, params)
	except Exception,e:
		print str(e)
		return None
	return True


def create_db(**kwargs):
    db = DB(mysqldb_user, mysqldb_password,mysqldb_host,mysqldb_db)
    tabname = t_vm
    time  =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tab_para = "(hostname,node,state,interval_time,update_time,create_time)"
    params = 'where hostname = "%s" and node = "%s"' % (kwargs['hostname'],kwargs['node'])
    try:
        if not db._select_(tabname,'hostname',params):
            db._insert_(tabname,tab_para,kwargs['hostname'],
                    kwargs['node'],kwargs['state'],kwargs['interval_time'],time,time)
    except Exception,e:
            print str(e)
            return None
    return True

def update_db(**kwargs):
    db = DB(mysqldb_user, mysqldb_password,mysqldb_host,mysqldb_db)
    tabname = t_vm
    



def del_db(**kwargs):
	tabname = t_vm
	tab_para = 'where hostname = "%s"' % kwargs['hostname']
	try:
		db = DB(mysqldb_user, mysqldb_password,mysqldb_host,mysqldb_db)
		db._del_(tabname, tab_para)
	except Exception,e:
		print str(e)
		return None
	return True

def  select_db():
	type_list = []
	result_dict = {}
	tabname = t_vm
	db = DB(mysqldb_user, mysqldb_password,mysqldb_host,mysqldb_db)
	# get node type
	for i in db._select_many_(tabname, "node", "group by node"):
		type_list.append(i['node'])
	for node in type_list:
		data_dict = {}
		try:
			data_list_60 = [k['hostname'] for  k in db._select_many_(tabname, "hostname",'where node="%s" and interval_time=%d' % (node,60))]
		except Exception:
			data_list_60 = None
		try:
			data_list_300 = [k['hostname'] for k in db._select_many_(tabname, "hostname",'where node="%s" and interval_time=%d' % (node,300))]
		except Exception:
			data_list_300 = None
		data_dict['60'] = data_list_60
		data_dict['300'] = data_list_300
		result_dict[node] = data_dict
	return result_dict

### import:::	url  i s based on hostname
def  process_handler(node,interval_time,instance_list):
	url = "http://node:9193/vm_monitor" % node
	while True:
    		inform_compute(url, instances_list)
		time.sleep(interval_time)
	return True

def main():
	node_dict = select_db()
	for node in node_dict:
		interval_dict = node_dict[node]
		for  interval in interval_dict:
			instance_list = interval_dict[interval]
			p = Process(name=process_handler,args=(node,interval,instance_list))
			p.start()
			p.join(0.00001)
	return True

		 


#### inform computeL
def inform_compute(url,instances_list):
	rep = requests.post(url)
	data = {'instances_list': instances_list}
	if  rep.status_code != requests.codes.ok:
		rep = requests.post(url, data=json.dumps(data))

	        if  rep.status_code != requests.codes.ok:
	        	return  None
	return True



@app.route("/vm/create",methods=['POST'])
def  vm_create():
	hostname = request.form['hostname']
	node = request.form['node']
	state = int(request.form['state'])
	interval = int(request.form['interval'])
	update_db(hostname=hostname,node=node,state=state,interval_time=interval)
	main()
	return jsonify(msg='success')

#@app.route("/vm/update",methods=['POST'])


@app.route("/vm/del",methods=['POST'])
def vm_del():
	hostname = request.form['hostname']
	node = request.form['node']
	state = int(request.form['state'])
	del_db(hostname=hostname)
	main()
	return jsonify(msg='success')

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=9190,debug=True)

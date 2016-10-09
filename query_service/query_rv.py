#!/usr/bin/python2.7
import paramiko
import time
from flask import Flask,request,jsonify
import pprint
import json
import requests
from web import app
import config
username = config.user_compute
password = config.passwd_compute
remote_file = "/tmp/traffic_vr.txt"
file_list = config.controller_node
Time =  str(time.time()).split(".")[0]
histroy_url = "http://"+config.query_addr+":9966/graph/history"

#app=Flask(__name__)

def sync_file(ip_addr,local_file,remote_file):
    t = paramiko.Transport(ip_addr)
    t.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remote_file, local_file)
    t.close()


def file_handler(File):
## dict form:  {"r_id":{"net_id":{"t_flow":"","s_flow":""}}
    data_dict = {}
    with open(File) as f:
        for line in f.readlines():
            field = line.strip().split()
            route_id = field[0]
            netcard_id = field[1].split("/")[0]
            tx = field[1].split("/")[1]
            value = field[2]
            time_now = field[3]
            if route_id  in data_dict:
                    if netcard_id in data_dict[route_id]:
                        data_dict[route_id][netcard_id][tx] = value
                    else:
                        data_dict[route_id][netcard_id]={tx:value}
                        #data_dict[route_id].append({netcard_id:{tx:flow}})
            else:
                data_dict[route_id]={netcard_id:{tx:value}}
    return data_dict,time_now


def data_handler(org_dict,time_now):
    data_dict = {}
    for route in org_dict:
        if "qrouter" in route:
            data_dict["is_rv"] = True
        else:
            data_dict["is_rv"] = False
        data_dict["route_id"] = route
        data_dict["flow"] = []
        net_dict = org_dict[route]
        for net in net_dict:
            temp_dict = {}
            rx = net_dict[net]["rx_bytes"]
            tx = net_dict[net]["tx_bytes"]
            temp_dict["netcard_id"] = net
            temp_dict["get_flow"] = rx
            temp_dict["send_flow"] = tx
            data_dict["flow"].append(temp_dict)
    data_dict["last_check"] = time_now
    return data_dict






def  main_file():
    data_dict = {}
    file_dict = {}
    data_list = []
## get file from remote server
    for ip_addr in file_list:
        local_file = ip_addr + '_vr.txt'
        sync_file(ip_addr, local_file, remote_file)
        temp_dict,time_now = file_handler(local_file)
        file_dict.update(temp_dict)
    for route in file_dict:
        data_dict = data_handler({route:file_dict[route]}, time_now)
        data_list.append(data_dict)
    return data_list

def query_one_hour_data():
    data_dict = {}
    data_list = []
    tags = 'function=vr_route,module=service'
    for ip_addr in file_list:
        local_file = ip_addr + '_vr.txt'
        ## sync data
        sync_file(ip_addr, local_file, remote_file)
        with open(local_file) as f:
            for line in f.readlines():
                field = line.strip().split()
                endpoint = field[0]
                counter = field[1]
                data_dict["endpoint"] = endpoint
                data_dict["counter"] = counter+'/'+tags
                print data_dict
                data_list.append(data_dict)
    end = int(Time)
    start = end - 60
    cf = "AVERAGE"
    data={"start":start,"end":end,"cf":cf,"endpoint_counters":data_list}
    try:
        rep = requests.post(histroy_url,data=json.dumps(data))
    except Exception,e:
        print str(e)
        return None
    return rep.text

def query_data(route,netcard):
    data_list = []
    tx_list = []
    rx_list = []
    end = int(Time)
    start = end - 3600
    cf = "AVERAGE"
    tags = 'function=vr_route,module=service'
    endpoint = route
    for ip_addr in file_list:
        local_file = ip_addr + '_vr.txt'
        ## sync data
        sync_file(ip_addr, local_file, remote_file)

    for flag in ["rx_bytes","tx_bytes"]:
        data_dict = {}
        data_dict["endpoint"] = endpoint
        counter = netcard + '/' + flag
        data_dict["counter"] = counter+'/'+tags
        data_list.append(data_dict)
    data={"start":start,"end":end,"cf":cf,"endpoint_counters":data_list}
    try:
        rep = requests.post(histroy_url,data=json.dumps(data))
    except Exception,e:
        print str(e)
        return None
    result =  json.loads(rep.text)
   # print "##########################"
  #  print result
    for i in result:
        temp_dict = {}
        try:
            t = i["counter"].split("/")[1]
        except Exception,e:
            print str(e)
            return None
        #print temp_dict
        if t == "rx_bytes":
            rx_list = i["Values"]
        else:
            tx_list = i["Values"]
    rx_list.sort(key=lambda obj:obj.get("timestamp"))
    tx_list.sort(key=lambda obj:obj.get("timestamp"))
    result_dict = {}
    result_dict["get_flow"] = rx_list
    result_dict["send_flow"] = tx_list
    return result_dict



@app.route("/vr/last")
def get_vr_last():
    result = main_file()
    return jsonify(pm_routes=result),202

@app.route("/vr/one-hour",methods=['POST'])
def get_vr_one_hour():
    endpoint = request.form["route_id"].strip()
    counter = request.form["netcard_id"].strip()
    result = query_data(endpoint, counter)
    if not result:
        return jsonify(msg="route or net not exsit"),404
    return json.dumps(result),200
    #result = query_one_hour_data()
#if __name__ == "__main__":
#    app.run(host="0.0.0.0",port=10040,debug=True)

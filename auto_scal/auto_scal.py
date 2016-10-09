#!/usr/lib/python2.7
# provide api for requesting which auto scaling
# the api packing original api
# request example: ['192.168.1.1','192.168.1.2']
import requests
import json
from flask import Flask,jsonify,request as flask_request
import config
def request_handler(ip_addr):
    url = "http://"+config.query_addr+":9966/graph/last"
    data = []
    metrics = ["num_requests/module=log,service=nginx","aver_resp_time/module=log,service=nginx"]
    for i in metrics:
        data_dict = {}
        data_dict["endpoint"] = ip_addr
        data_dict["counter"] = i
        data.append(data_dict)
    try:
        rep = requests.post(url,data=json.dumps(data))
        print rep.text
    except Exception,e:
        print str(e)
        return None
    else:
        result_dict = {}
        result_dict['ip'] = ip_addr
        for i in json.loads(rep.text):
            result_dict[i["counter"]] = i["value"]["value"]
        return result_dict


def load_banlance(ip_addr):
    url = "http://"+config.query_addr+":9966/graph/last"
    data = []
    metrics = ["num_requests/module=log,service=nginx","aver_resp_time/module=log,service=nginx"]
    for i in metrics:
        data_dict = {}
        data_dict["endpoint"] = ip_addr
        data_dict["counter"] = i
        data.append(data_dict)
    try:
        rep = requests.post(url,data=json.dumps(data))
        print rep.text
    except Exception,e:
        print str(e)
        return None
    else:
        result_dict = {}
        result_dict['ip'] = ip_addr
        for i in json.loads(rep.text):
            metric = i["counter"].split("/")[0]
            result_dict[metric] = i["value"]["value"]
            result_dict["timestamp"] = i["value"]["timestamp"]
        return result_dict



            
app = Flask(__name__)

@app.route("/auto_scalling",methods=['POST'])
def main():
    data_list = []
    try:
        temp_dict = json.loads(flask_request.data)
        ip_list = temp_dict["ip_list"]
    except Exception,e:
        return jsonify(msg=str(e)),500
    for ip in ip_list:
        ip_data_dict = request_handler(ip)
        data_list.append(ip_data_dict)
    return jsonify(msg="",data=data_list)

## request params: ["122.115.51.8:80","122.115.51.9:80"]
# return: [{"ip":"122.115.51.8:80","num_requests":122,"aver_resp_time":321.1,"timestamp":122111441}]
@app.route("/load-monitor",methods=['POST'])
def load():
    data_list = []
    ipaddrs = json.loads(flask_request.data)
    for ip in ipaddrs:
        print ip
        data_dict = {}
        data_dict = load_banlance(ip)
        if not data_dict:
	    continue
        data_list.append(data_dict)
    return json.dumps(data_list),200
        
    
    

@app.route("/health")
def test():
    return "ok"

if __name__ == '__main__':
# test
    app.run(host="0.0.0.0",port=9900,debug=True)
    

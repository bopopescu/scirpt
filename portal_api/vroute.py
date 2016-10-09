### api virtual route
from db import DB
import requests
import json
from flask import *
from portal_api import app

qurl = "http://127.0.0.1:9966/graph/last"

## get all nic with vroute
def NicVroute(sid):
    # pre = "qroute-"
    # endpoint = pre+id
    handler = DB("falcon","password","127.0.0.1","graph")
    end_id = handler._select_("endpoint", "id",'where endpoint="%s"' % sid)
    if not end_id:
        abort(404)
    end_id = end_id['id']
    nics = handler._select_many_("endpoint_counter", "counter","where endpoint_id=%d" % int(end_id))
    result = [i["counter"] for i in nics]
#return nic list
    return result
## request query and get  data
def GetData(sid):
    result_list = []
    data_list = []
    pre = "qrouter-"
    endpoint = pre+sid

    nics = NicVroute(endpoint)
    print nics
    for nic in nics:
        data_dict = {}
        data_dict["endpoint"] = endpoint
        data_dict["counter"] = nic
        data_list.append(data_dict)
 
    rep = requests.post(qurl,data=json.dumps(data_list))
    result = json.loads(rep.text)
    for i in result:
        result_dict = {}
        result_dict["endpoint"] = i["endpoint"]
        counter = i["counter"].split("/")
        result_dict["counter"] = counter[0]
        result_dict["tx"] = counter[1]
        result_dict["timestamp"] = i["value"]["timestamp"]
        result_dict["value"] = i["value"]["value"]
        result_list.append(result_dict)
    return result_list

## provide api
@app.route("/vroute/<sid>")
def vroute(sid):
    result = GetData(sid)
    return json.dumps(result),200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8001,debug=True)

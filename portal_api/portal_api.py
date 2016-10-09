#!/usr/bin/pyhton2.7
import json
from flask import Flask,jsonify,abort,request
from port_model import ApiPortal
from vm_handler import SQLHandler
from time import time
from logger import Logger
import os


dirname = os.path.dirname(os.path.abspath(__file__))
log = Logger(debug=True,filename=os.path.join(dirname,"app.log"))



app = Flask(__name__)
import vroute
@app.errorhandler(404)
def page_not_found(error):
    return jsonify(msg="page not found"),404

@app.errorhandler(500)
def server_error(error):
    return jsonify(msg="interal server error"),500

## create alarm startegy
@app.route("/alarm-strategy/create",methods=['POST'])
def create_template():
    handler = ApiPortal()   ####### need  review !!!
    rep_data = json.loads(request.data)
    tem = rep_data["name"].strip()
    interval = rep_data["interval"].strip()
    print tem
    print interval
    #create template
    if not handler.api_create_template(tem,interval):
        abort(500)
    # create host group,the name is same with template
    if not _create_host_group(tem):
        abort(500)
    # link host group with template
    if not _bind_template_group(tem, tem):
        abort(500)
    data = handler.api_get_template(tem)
    return jsonify(msg='success',data = data, action= "create"),200


## delete alarm startegy
@app.route("/alarm-strategy/delete",methods=['POST'])
def delete_template():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    tem = rep_data["name"].strip()
    data = handler.api_get_template(tem)
    if not data:
        abort(404)
    # unlink host group with template
    if not _unbind_template_group(tem,tem):
        abort(500)
    # remove host group
    if not _delete_host_group(tem):
        abort(500)
    # remove template
    if not handler.api_delete_template(tem):
        abort(500)
    return jsonify(msg="success",data=data,action="delete"),200

## update  alarm strategy
@app.route("/alarm-strategy/update",methods=['POST'])
def update_template():
    handler = ApiPortal()
    handler_vm = SQLHandler()
    rep_data = json.loads(request.data)
    tem_name = rep_data["name"].strip()
    new_name = rep_data["new_name"].strip()
    interval = rep_data["interval_time"].strip()
    interval_begin = handler.api_get_template_interval(tem_name)
    host_list = handler.api_get_host_from_template(tem_name)
    if int(interval_begin) != int(interval):
        if host_list:
            for host in host_list:
                handler_vm.update_db("interval_time",interval_time=interval,hostname=host)
    if not handler.api_update_template(tem_name, new_name, interval):
        abort(500)
    data = handler.api_get_template(new_name)
    return jsonify(msg="success",data=data,action="update"),200

## get alarm strategy
@app.route("/alarm-strategy/get/<tem_name>")
def get_template(tem_name):
    handler = ApiPortal()
    data = handler.api_get_template(tem_name)
    if not data:
        abort(404)
    return jsonify(msg="success",data=data),200

## create alarm rule
@app.route("/alarm-rule/create",methods=['POST'])
def create_strategy():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    metric = rep_data["metric"].strip()
    op = rep_data["op"].strip()
    right_value = rep_data["right_value"].strip()
    period  = rep_data["period"].strip()
    tem_name = rep_data["name"].strip()
    actions = "all"
    data = handler.api_add_strategy(metric=metric,op=op,right_value=right_value,
            period=period,tem_name=tem_name,actions=actions)
    if not data:
        abort(500)
    return jsonify(msg="success",data=data,action="create"),200

## create alarm rule list
@app.route("/alarm-rule-list/create",methods=['POST'])
def create_strategy_list():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    data_list = rep_data["data_list"].strip()
    tem_name = rep_data["tem_name"].strip()
    actions = rep_data["actions"].strip()
    data = handler.api_add_strategy_list(data_list, tem_name, actions)
    if not data:
        abort(500)
    return jsonify(msg="success",data=data,action="create"),200

## delete alarm rule
@app.route("/alarm-rule/delete/<sid>")
def delete_strategy(sid):
    handler = ApiPortal()
    data = handler.api_get_strategy(sid)
    if not data:
        abort(404)
    rep = handler.api_delete_strategy(sid)
    if not rep:
        abort(500)
    return jsonify(msg="success",data=data,action="delete"),200

## update alarm rule
@app.route("/alarm-rule/update",methods=['POST'])
def update_strategy():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    sid = rep_data["sid"].strip()
    metric = rep_data["metric"].strip()
    op = rep_data["op"].strip()
    right_value = rep_data["right_value"].strip()
    if not handler.api_get_strategy(sid):
        abort(404)
    if not handler.api_update_strategy(sid, metric, op, right_value):
        abort(500)
    data = handler.api_get_strategy(sid)
    return  jsonify(msg="success",data=data,action="update"),200

## get alarm rule
@app.route("/alarm-rule/get/<sid>")
def get_strategy(sid):
    handler = ApiPortal()
    data = handler.api_get_strategy(sid)
    if not data:
        abort(404)
    return  jsonify(msg="success",data=data),200




## create inform-list
@app.route("/inform-list/create",methods=['POST'])
def create_uic_group():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    action = rep_data["action"].strip()
    if not handler.api_add_uic_group(grp_name,action):
        abort(500)
    return jsonify(msg="success",action="create"),200

## delete inform-list
@app.route("/inform-list/delete",methods=['POST'])
def delete_uic_group():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    if not handler.api_delete_uic_group(grp_name):
        abort(500)
    return jsonify(msg="success",action="delete"),200

## update inform-list
@app.route("/inform-list/update",methods=["POST"])
def update_uic_group():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    action = rep_data["action"].strip()
    if not handler.api_update_uic_group(grp_name,action):
        abort(500)
    return jsonify(msg="success",action="update"),200


## get inform-list
@app.route("/inform-list/get/users/<grp_name>")
def get_uic_group(grp_name):
    handler = ApiPortal()
    data = handler.api_get_users_from_group(grp_name)
    if not data:
        abort(404)
    return jsonify(msg="success",data=data),200



## create user
@app.route("/user/create",methods=['POST'])
def create_uic_user():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    user = rep_data["user"].strip()
    email = rep_data["email"].strip()
    phone = rep_data["phone"].strip()

    if not handler.api_create_user(grp_name, user, email, phone):
        abort(500)
    data = handler.api_get_user(user)
    if not data:
        abort(404)
    return jsonify(msg="success",action="create",data=data),200

## delete user
@app.route("/user/delete",methods=['POST'])
def  delete_uic_user():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    user = rep_data["user"].strip()
    if not handler.api_delete_user(grp_name, user):
        abort(500)
    return jsonify(msg="success",action="delete"),200

## update user
@app.route("/user/update",methods=['POST'])
def update_uic_user():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    user = rep_data["user"].strip()
    email = rep_data["email"].strip()
    phone = rep_data["phone"].strip()

    if not handler.api_get_user(user):
        abort(404)
    if not handler.api_update_uic_user(user, email, phone):
        abort(500)
    data = handler.api_get_user(user)
    return jsonify(msg="success",action="update",data=data),200


# get user
@app.route("/user/get/<user>")
def get_uic_user(user):
    handler = ApiPortal()
    data = handler.api_get_user(user)
    if not data:
        abort(404)
    return jsonify(msg="success",data=data),200



#bind inform-list to alarm-strategy   params: all group
@app.route("/actions/update",methods=['POST'])
def update_actions():
    handler = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["informs"].strip()
    tem_name = rep_data["name"].strip()
    # actions = rep_data["actions"].strip()

    if not handler.api_get_template(tem_name):
        abort(404)
    if not handler.api_update_user_strategy(grp_name, tem_name):
        abort(500)
    return jsonify(msg="success",action="update"),200

# create resource list
#@app.route("/resouce-list/create",methods=['POST'])
def _create_host_group(grp_name):
    handler = ApiPortal()
    #grp_name = request.form["resource_name"].strip()
    if not handler.api_create_group(grp_name):
        abort(500)
    data = handler.api_get_group(grp_name)
    #return jsonify(msg="success",action="create",data= data),200
    return True

# delete resource list
#@app.route("/resouce-list/delete",methods=['POST'])
def _delete_host_group(grp_name):
    handler = ApiPortal()
#    grp_name = request.form["resource_name"].strip()
    if not handler.api_get_group(grp_name):
        abort(404)
    if not handler.api_delete_group(grp_name):
        abort(500)
    #return jsonify(msg="success",action="delete"),200
    return True

# get resource list
#@app.route("/resouce-list/get/<grp_name>")
def _get_host_group(grp_name):
    handler = ApiPortal()
    data = handler.api_get_group(grp_name)
    if not data:
        abort(404)
    #return jsonify(msg="success",data= data),200
    return data

# insert host into resource-list
#@app.route("/host/bind/resource",methods=['POST'])
def _insert_host_group(grp_name,host):
    handler = ApiPortal()
    #grp_name = request.form["resource_name"].strip()
    #host = request.form["host"].strip()
    if not handler.api_get_hostgroup(host,grp_name):

        if not handler.api_bind_host_group(grp_name,host):
            return None
        else:
            return True
    #return jsonify(msg="success",action="create"),200
    return None

# pop host from resource-list
#@app.route("/host/unbind/resource",methods=['POST'])
def _pop_host_group(grp_name,host):
    handler = ApiPortal()
    host_handler = SQLHandler()
    #grp_name = request.form["resource_name"].strip()
    #host = request.form["host"].strip()
    host_id = host_handler.get_host(host)
    #print 20*'#',"host_id:",host_id
    # if handler.api_get_hostgroup(host, grp_name):

    handler.api_unbind_host_group(grp_name,host_id)
    return True
    #return jsonify(msg="success",action="delete"),200
    #return None

# bind stategy list on resource list
#@app.route("/strategy/bind/resource",methods=['POST'])
def _bind_template_group(tpl_name,grp_name):
    handler = ApiPortal()
    #tpl_name = request.form["stra_name"].strip()
    #grp_name = request.form["res_name"].strip()
    if not handler.api_bind_template_group(tpl_name,grp_name):
        abort(500)
    #return jsonify(msg="success",action="bind"),200
    return True

# unbind strategy list from resource
#@app.route("/strategy/unbind/resource",methods=['POST'])
def _unbind_template_group(tpl_name,grp_name):
    handler = ApiPortal()
    #tpl_name = request.form["stra_name"].strip()
    #grp_name = request.form["res_name"].strip()
    if not handler.api_unbind_template_group(tpl_name,grp_name):
        abort(500)
    #return jsonify(msg="success",action="unbind"),200
    return True


# add virtual host    
@app.route("/vm/add",methods=['POST'])
def add_vm():
    handler = SQLHandler()
    handler_model = ApiPortal()
    rep_data = json.loads(request.data)
    hostname = rep_data["hostname"].strip()
    node = rep_data["node"].strip()
    #tem_name = rep_data["stra_name"].strip()
    uuid = rep_data["uuid"].strip()
    #interval_time = handler_model.api_get_template_interval(tem_name) or 300
    interval_time = 300
    #ip = request.form["ip"].strip()
    #state = request.form["state"].strip()
    ip = "192.168.1.1"
    state = 1
##### add  instance in table vm_host
    if not handler.update_db(hostname=hostname,node=node,interval_time=int(interval_time),
            uuid=uuid, state=state):
        abort(500)
######## add instance in table host
    handler.create_host(hostname,ip)
# add host in host group
    #_insert_host_group(tem_name,hostname)
    return jsonify(msg="success",action="create"),200

# delete virtual host
@app.route("/vm/delete",methods=['POST'])
def delete_vm():
    handler = SQLHandler()
    handler2 = ApiPortal()
    rep_data = json.loads(request.data)
    host_id = int(rep_data["hostname"].strip())
    log.debug( "------------------%s" % host_id)
    #grp_name = rep_data["stra_name"].strip()
    # remove host from host group
  #  _pop_host_group(grp_name,hostname)
    # remove instance from table vm_host
    if not handler2.api_get_host_fromgroup(host_id):
        hostname = handler.get_host_name_where_id(host_id)
        log.debug("-------------delvm host rows:%s" % hostname)
	handler.del_db(hostname)
    # remove instance from table host
       # handler.delete_host(hostname)
    return jsonify(msg="success",action="delete"),200

#add many vms
@app.route("/vm/add-many",methods=['POST'])
def add_many_vm():
    #### params: {"stra_name":"template_name","instances":[{"hostname":"hostname", "node":"compute01"}]}
    handler = SQLHandler()
    handler_model = ApiPortal()
    rep_data = json.loads(request.data)
    tem_name = rep_data["stra_name"].strip()
    instances_list = rep_data["instances"]
    state = 1
    ip = "192.168.1.1"
    interval_time = handler_model.api_get_template_interval(tem_name) or 300
    for instance in instances_list:
        ## instance is dict
        hostname = instance["hostname"]
        node = instance["node"]
        uuid = instance["uuid"]
        if not handler.update_db(hostname=hostname,node=node,interval_time=int(interval_time),
            uuid=uuid, state=state):
            abort(500)
######## add instance in table host
        handler.create_host(hostname,ip)
# add host in host group
        _insert_host_group(tem_name,hostname)
    return jsonify(msg="success",action="create"),200

# del many vms
@app.route("/vm/delete-many",methods=['POST'])
def delete_many_vm():
    handler = SQLHandler()
    handler_model = ApiPortal()
    rep_data = json.loads(request.data)
    grp_name = rep_data["stra_name"].strip()
    instances_list = rep_data["instances"]

    for hostname in instances_list:
        _pop_host_group(grp_name,hostname)
        if not handler_model.api_get_host_fromgroup(hostname):
    # remove instance from table vm_host
            handler.del_db(hostname)
    # remove instance from table host
            handler.delete_host(hostname)
    return jsonify(msg="success",action="delete"),200


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=10020,debug=True)














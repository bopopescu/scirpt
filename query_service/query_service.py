#!/usr/bin/python2.7
#author: zhanghao
#date: 2015-11-23
#version: 0.0
#func: provide api for oss with service monitor
## request form: {"pm_service":[{"host_name":"0.0.0.0","port":"8000","service_type":""},
##  {"host_name":"0.0.0.1","port":8001,"service_type":""}]}
## response form: {"pm_service":[{"host_name":"0.0.0.0","port":"8000","service_type":"","status":null,
##      "performance":null,"last_check":null},{"host_name":"0.0.0.0","port":"8000","service_type":"",
##      "status":null,"performance":null,"last_check":null}]}

import json
import requests
from flask import Flask,jsonify,request
from web import app
import config
url = "http://"+config.query_addr+":9966/graph/last"
#mysql metric
mysql_metrics = ['mysql.QPS','mysql.Aborted_connects','mysql.Binlog_cache_disk_use',
'mysql.Bytes_received','mysql.Bytes_sent','mysql.Connections','mysql.Created_tmp_disk_tables',
'mysql.Created_tmp_files','mysql.Created_tmp_tables','mysql.Handler_delete','mysql.Handler_read_first',
'mysql.Handler_read_rnd','mysql.Handler_read_rnd_next','mysql.Handler_update','mysql.Handler_write',
'mysql.Key_read_requests','mysql.Key_reads','mysql.Max_used_connections','mysql.Open_files',
'mysql.Opened_table_definitions','mysql.Opened_tables','mysql.Opened_tables','mysql.Qcache_free_memory',
'mysql.Qcache_hits','mysql.Qcache_queries_in_cache','mysql.Questions','mysql.Select_full_join',
'mysql.Select_full_range_join','mysql.Select_range','mysql.Select_range_check','mysql.Select_scan',
'mysql.Slave_running','mysql.Slow_queries','mysql.Sort_merge_passes','mysql.Sort_scan',
'mysql.Table_locks_immediate','mysql.Table_locks_waited','mysql.Threads_connected',
'mysql.Threads_created','mysql.Threads_running','mysql.Uptime','mysql.port.listen_3306']

#memcache metric
memcache_metrics = ['memcache.statdel_hit_value','memcache.statget_hit_value',
    'memcache.statset_total_value','memcache.reqrate_cas_value','memcache.statget_total_value',
    'memcache.statauth_errors_value','memcache.reqrate_decr_value','memcache.statcas_badval_value',
    'memcache.connrate_conn_value','memcache.items_items_value','memcache.reqrate_get_value',
    'memcache.statcas_total_value','memcache.statincrdecr_incr_miss_value','memcache.hitpct_incr_value',
    'memcache.statcas_hit_value','memcache.reqrate_incr_value','memcache.hitpct_get_value',
    'memcache.statincrdecr_total_value','memcache.statincrdecr_decr_hit_value','memcache.hitpct_set_value',
    'memcache.hitpct_cas_value','memcache.statincrdecr_decr_miss_value','memcache.statdel_total_value',
    'memcache.statauth_reqs_value','memcache.statevict_evict_value','memcache.statcas_miss_value',
    'memcache.statdel_miss_value','memcache.connections_conn_value','memcache.reqrate_set_value',
    'memcache.statset_hit_value','memcache.memory_bytes_value','memcache.hitpct_decr_value',
    'memcache.statget_miss_value','memcache.traffic_rxbytes_value','memcache.reqrate_del_value',
    'memcache.traffic_txbytes_value','memcache.hitpct_del_value','memcache.statevict_reclaim_value',
    'memcache.statincrdecr_incr_hit_value','memcache.statset_miss_value','memcache.port.listen_11211']

#haproxy metric
haproxy_metrics = ['haproxy.current_queued_request','haproxy.current_sessions','haproxy.bytes_in',
    'haproxy.bytes_out','haproxy.request_errors','haproxy.connection_errors','haproxy.status',
    'haproxy.num_fail_check','haproxy.num_down_check','haproxy.request_rate']

#rabbitmq metric
rabbit_metrics = ['rabbitmq.rabbitmq_uptime','rabbitmq.rabbitmq_messages','rabbitmq.rabbitmq_ack',
    'rabbitmq.rabbitmq_deliver_get','rabbitmq.rabbitmq_deliver','rabbitmq.rabbitmq_sockets_total',
    'rabbitmq.rabbitmq_publish','rabbitmq.rabbitmq_fd_used','rabbitmq.rabbitmq_mem_used',
    'rabbitmq.rabbitmq_fd_total','rabbitmq.rabbitmq_disk_free_alarm_status','rabbitmq.rabbitmq_proc_used',
    'rabbitmq.rabbitmq_mem_limit','rabbitmq.rabbitmq_mem_alarm_status','rabbitmq.rabbitmq_sockets_used',
    'rabbitmq.rabbitmq_messages_unacknowledged','rabbitmq.rabbitmq_messages_ready',
    'rabbitmq.rabbitmq_proc_total','rabbit.rabbit_local_status','rabbit.port.listen_4369',
    'rabbit.port.listen_15672']

#apache metric
apache_metrics = ['apache.port.listen_80','apache.access_reqs_value','apache.bytes_bytes_value',
    'apache.workers_busy_value','apache.workers_idle_value','apache.worksers_max_value']

#keystone
keystone_metrics = ['key.port.listen_5000','key.port.listen_35357','key.api.auth_status','key.log.local_api_resp_time',
                    'key.api.num_users','key.api.num_tenants']
#nova
nova_metrics = ['nova.port.listen_8774','nova.pro.nova_api','nova.pro.nova_scheduler','nova.pro.nova_consoleauth',
    'nova.pro.nova_console','nova.pro.nova_novncproxy','nova.pro.nova_cert','nova.pro.nova_compute',
    'nova.api.api_nova_status','nova.api.api_local_api_resp_time','nova.api.num_instance/state=error',
    'nova.api.num_instance/state=stopped','nova.api.num_instance/state=running',
    'nova.api.metadata_nova_status','nova.api.metadata_nova_resp_time','nova.api.register_nova_scheduler',
    'nova.api.register_nova_consoleauth','nova.api.register_nova_novncproxy','nova.api.register_nova_cert',
    'nova.api.register_nova_compute']

##glance
glance_metrics = ['glance.port.listen_9292','glance.port.listen_9191','glance.api.num_active_images','glance.api.num_killed_images',
    'glance.api.num_queued_images','glance.api.api_local_api_resp_time','glance.api.api_local_status',
    'glance.api.register_local_status','glance.api.register_local_api_resp_time']

#cinder
cinder_metrics = ['cinder.port.listen_8776','cinder.pro.cinder_api','cinder.pro.cinder_scheduler',
    'cinder.pro.cinder_volume','cinder.api.api_local_status','cinder.api.api_local_api_resp_time',
    'cinder.api.total_volumes','cinder.api.available_volumes','cinder.api.in-use_volumes',
    'cinder.api.error_volumes','cinder.api.total_snapshots','cinder.api.available_snapshots',
    'cinder.api.in-use_snapshots','cinder.api.error_snapshots']

#neutron
neutron_metrics = ['neutron.port.listen_9696','neutron.pro.neutron_server','neutron.pro.neutron_dhcp_agent',
    'neutron.pro.neutron_l3_agent','neutron.pro.neutron_metadata_agent',
    'neutron.pro.neutron_ns_metadata_proxy','neutron.pro.neutron_openvswitch_agent','neutron.pro.dnsmasq',
    'neutron.api.local_status','neutron.api.local_api_resp_time','neutron.api.neutron_networks',
    'neutron.api.neutron_agents','neutron.api.neutron_routers','neutron.api.neutron_subnets',
    'neutron.api.neutron_openvswitch_status_{host}','neutron.api.neutron_l3_status_{host}',
    'neutron.api.neutron_dhcp_status_{host}','neutron.api.neutron-metadata_status_{host}']

#horizon
horizon_metrics = ['horizon.port.listen_80','horizon.api.horizon_local_status','horizon.api.horizon_status_code',
    'horizon.api.horizon_api_resp_time','horizon.api.horizon_login_status_code',
    'horizon.api.horizon_login_resp_time']

def query_data(hostname,metric_type):
    data = []
    if metric_type == 'mysql':
        metrics = mysql_metrics
    elif metric_type == 'memcache':
        metrics = memcache_metrics
    elif metric_type == 'haproxy':
        metrics = haproxy_metrics
    elif metric_type == 'rabbit':
        metrics = rabbit_metrics
    elif metric_type == 'apache':
        metrics = apache_metrics
    elif metric_type == 'keystone':
        metrics = keystone_metrics
    elif metric_type == 'nova':
        metrics = nova_metrics
    elif metric_type == 'glance':
        metrics = glance_metrics
    elif metric_type == 'cinder':
        metrics = cinder_metrics
    elif metric_type == 'neutron':
        metrics = neutron_metrics
    elif metric_type == 'horizon':
        metrics = horizon_metrics
    else:
        return None
    for metric in metrics:
        metric = metric + '/function=%s,module=service' % metric_type
        data_metric = {"endpoint":hostname,"counter":metric}
        data.append(data_metric)
    rep = requests.post(url,data=json.dumps(data))
    return json.loads(rep.text)

def  main(data):
    result = []
    data_dict = {}
    for service in data["pm_service"]:
        hostname = service["host_name"]
        port = service["port"]
        service_type = service["service_type"]
        rep = query_data(hostname,service_type)
        if not rep:
            print "Err,Not service type!"
 	    return None
        data_dict = handler_data(rep,port)
        data_dict["service_type"] = service_type
        result.append(data_dict)
    return result

def handler_data(data,port):
    data_dict = {}
    perfarmance_dict = {}
    for i in data:
        hostname = i["endpoint"]
        metric = i["counter"]
        value = i["value"]["value"]
        string_port = "listen_" + port
        if string_port in metric:
            status = int(value)
            timestamp = i["value"]["timestamp"]
        else:
            perfarmance_dict[metric] = value
    try:
        data_dict["status"] = status
        data_dict["last_check"] = timestamp
    except Exception,e:
        print str(e)
        return None
    data_dict["port"] = port
    data_dict["host_name"] = hostname
    data_dict["perfarmance"] = perfarmance_dict
    return data_dict


@app.route("/services/showing",methods=['POST'])
def service_show():
#    Data = request.form["pm_service"].strip()
    Data = request.data
    data = json.loads(Data)
    print "####"
    print data
    result = main(data)
    if not result:
	return jsonify(msg="service not exist"),404
    return jsonify(pm_service=result),200

@app.route("/test")
def test():
    return "test!"

#if __name__ == '__main__':
#  app.run(hostname="0.0.0.0",port=10030,debug=True)
#  data={"pm_service":[{"host_name":"controller-02","port":"3306","service_type":"mysql"},{"host_name":"controller-02","port":"80","service_type":"apache"}]}
#  result = main(data)
#  print result




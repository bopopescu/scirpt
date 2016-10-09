#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import requests
import os
import json
import pprint
def get_auth_details(openrc_file):
    auth_details = {}
    pattern = re.compile('^(?:export\s)?(?P<key>\w+)(?:\s+)?=(?:\s+)?(?P<value>.*)$')
    try:
        with open(openrc_file) as openrc:
            for line in openrc:
                match = pattern.match(line)
                if match is None:
                    continue
                k = match.group('key')
                v = match.group('value')
                auth_details[k] = v
    except Exception,e:
        print str(e)
        return None
    return auth_details

class GetVMs():
    def __init__(self,get_auth):
        self.username = get_auth['OS_USERNAME']
        self.password = get_auth['OS_PASSWORD']
        self.tenant = get_auth['OS_TENANT_NAME']
        self.auth_url = get_auth['OS_AUTH_URL']

    def GetToken(self):
        token_url = self.auth_url+'/tokens'
        token_header = {'Content-type': 'application/json'}        
        token_data = {"auth": {"tenantName": self.tenant, "passwordCredentials": {"username": self.username, "password": self.password}}}
        res = requests.post(token_url,data=json.dumps(token_data),headers=token_header)
        return json.loads(res.text)

    def GetNovaList(self):
        data_list = []
        self.nova_url = self.GetToken()['access']['serviceCatalog'][0]['endpoints'][0]['adminURL'] + "/servers/detail"
        self.token = self.GetToken()['access']['token']['id']
        header = {'Content-type': 'application/json', 'x-auth-token': self.token}
        res = requests.get(self.nova_url,headers=header)
        datas =  json.loads(res.text)
        for i in datas['servers']:
            instance_name = i['OS-EXT-SRV-ATTR:instance_name']
            power_state = i['OS-EXT-STS:power_state']
            vm_state = i['OS-EXT-STS:vm_state']
            uuid = i['id']
            name = i['name']
            create_time = i['OS-SRV-USG:launched_at']
            update_time = i['updated']
            data_dict = {}
            data_dict['instance_name'] = instance_name
            data_dict['power_state'] = power_state
            data_dict['vm_state'] = vm_state
            data_dict['uuid'] = uuid
            data_dict['name'] = name
            data_dict['create_time'] = create_time
            data_dict['update_time'] = update_time
            data_list.append(data_dict)
        return data_list

if __name__ == '__main__':
    base_path = os.path.dirname(__file__)
    openrc_file = os.path.join(base_path,"admin.sh")
    auth_details = get_auth_details(openrc_file)
    vm_instance = GetVMs(auth_details)
    pprint.pprint(vm_instance.GetNovaList())

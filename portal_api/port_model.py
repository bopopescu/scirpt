#!/usr/bin/python2.7
import requests
import json
from logger import Logger
import os
import pdb

dirname = os.path.dirname(os.path.abspath(__file__))
log = Logger(debug=True,filename=os.path.join(dirname,"app.log"))


"""provide api for Portal"""



def login_falcon_portal():
    """
    user authorizoning
    """
    url = "http://127.0.0.1:1234/auth/login"
    s = requests.session()
    data = {"name":"root","password":"root"}
    rep = s.post(url,data=data)
### ps: add log for recording
## delete function that authorizoning user  ------- p2
    if json.loads(rep.text)["msg"] == "":
        return s
    else:
        return None

class ApiPortal():
    def __init__(self):
        self.session = login_falcon_portal()

    def api_create_template(self, tem_name,interval):
        #"create alarm strategy"
        #"create template"
        url = "http://127.0.0.1:5050/templates/create"
        data = {"tem_name":tem_name,"interval":interval}
        try:
            rep = self.session.post(url,data= data)
            log.debug(rep.text)
        except Exception,e:
            print str(e)
            return None
        return True


    def api_update_template(self, tem_name,new_name,interval):
        #"update alarm strategy"
        #"update template"

        tpl_id = self._get_template_id(tem_name)
        url = "http://127.0.0.1:5050/template/rename/%d" % tpl_id
        data = {"name":new_name}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
            return None
        url1 = "http://127.0.0.1:5050/template/update-time"
        data1 = {"tpl_id":tpl_id,"interval_time":interval}
        try:
            rep = self.session.post(url1,data=data1)
        except Exception,e:
            log.error(str(e))
            return None
        return True

    def api_delete_template(self, tem_name):
        #"delete alarm strategy"
        # delete template
        tpl_id = self._get_template_id(tem_name)
        url = "http://127.0.0.1:5050/template/delete/%d" % tpl_id
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
        return True
    def api_get_template(self,tem_name):
        url = "http://127.0.0.1:5050/template/get/info/%s" % tem_name
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
        return json.loads(rep.text)["data"][0]

    def api_get_template_interval(self,tem_name):
        url = "http://127.0.0.1:5050/template/get/info/%s" % tem_name
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
	if not json.loads(rep.text)["data"]:
		return None
        return json.loads(rep.text)["data"][0]["interval_time"]


    def api_add_strategy(self, **kwargs):
    # add strategy rule
    # create strategy
    #### params: metric, op, right_value, period, tem_name, action in type dict
        tpl_id = self._get_template_id(kwargs["tem_name"])
        url = "http://127.0.0.1:5050/strategy/update"
        tags = ""
        max_step = 5
        note = ""
        func = "all(#%s)" % kwargs["period"]
        run_begin = ""
        run_end = ""
        priority = self._calculate_priority(kwargs["actions"])
        tpl_id = self._get_template_id(kwargs["tem_name"])
        data = {"sid":"", "metric":kwargs["metric"],"tags":tags,"max_step":max_step,"priority":priority,
            "note":note,"func":func,"op":kwargs["op"],"right_value":kwargs["right_value"],"run_begin":run_begin,
            "run_end":run_end,"tpl_id": int(tpl_id)
            }
        try:
            rep = self.session.post(url,data=data)
        #sid = _get_strategy_sid(metric,op,right_value,tpl_id)
            sid = self._get_strategy_sid(kwargs['metric'],kwargs['op'],kwargs['right_value'],tpl_id)
        except Exception,e:
            log.error(str(e))
            return None
        return sid

    def api_update_strategy(self,**kwargs):
        ## params
        if 'sid' not in kwargs:
            print "sid not in params"
            return None
        sid = kwargs.pop('sid')
        url = "http://127.0.0.1:5050/strategy/update_params"
        data={"sid":sid,"params":kwargs}
        try:
            rep = self.session.post(url,data=data)
        except Exception,e:
            log.error(str(e))
            return None
        return True


    def api_add_strategy_list(self, data_list,tem_name,actions):
        # add strategy list
    ## params: data_list = [{"metric":"","op":"","right_value":""}], tem_name, actions
        sid_list = []
        tpl_id = self._get_template_id(tem_name)
        url = "http://127.0.0.1:5050/strategy/update"
        tags = ""
        max_step = 5
        note = ""
        func = "all(#3)"
        run_begin = ""
        run_end = ""
        priority = self._calculate_priority(actions)
        for i in data_list:
            data = {"sid":"","metric":i["metric"],"tags":tags,"max_step":max_step,"priority":int(priority),
            "note":note, "func":func,"op":i["op"], "right_value": i["right_value"], "run_begin":run_begin,
            "run_end": run_end, "tpl_id": int(tpl_id)}
            try:
                rep = self.session.post(url, data=data)
                sid = self._get_strategy_sid(i['metric'],i['op'],i['right_value'],tpl_id)
                sid_list.append(sid)
            except Exception,e:
                log.error(str(e))
        return sid_list



    def api_update_strategy(self,sid,metric,op,right_value):
        # update strategy
        url = "http://127.0.0.1:5050/strategy_new/update"
        data = {"sid":sid,"metric": metric, "op": op,"right_value": right_value}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True


    def api_delete_strategy(self,sid):
        # delete strategy
        url = "http://127.0.0.1:5050/strategy/delete/%d" % int(sid)
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
        return True       

    def api_get_strategy(self,sid):
        ## get strategy
        url = "http://127.0.0.1:5050/strategy/%d" % int(sid)
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
        return json.loads(rep.text)["data"]

    def _calculate_priority(self,actions):
        # get priority through actions
        "return priority"
        if actions == "mail":
            priority = 4
    ####ps: modify open-falcon source code
        elif actions == "sms":
            priority = 6
        elif actions == "all":
            priority = 2
        return priority


    def api_add_uic_group(self, grp_name,action):
    ## create inform list
    # create uic group
        url = "http://127.0.0.1:5050/uic/group/create"
        priority = self._calculate_priority(action)
        data = {"grp_name":grp_name,"grp_resume":"","action":str(priority)}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
            return None
        return True   

    def api_delete_uic_group(self, grp_name):
    ## delete inform list
    ## delete uic group
        url = "http://127.0.0.1:5050/uic/group/delete"
        grp_id = self._get_uic_group(grp_name)
        data = {"grp_id":grp_id}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True


    def api_update_uic_group(self, grp_name,new_action):
    ## delete inform list
    ## delete uic group
        url = "http://127.0.0.1:5050/uic/group/update"
        priority = self._calculate_priority(new_action)
        data = {"grp_name":grp_name,"action":priority}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True


    def api_get_users_from_group(self,grp_name):
        grp_id = self._get_uic_group(grp_name)
        url = "http://127.0.0.1:5050/uic/group/getuser/%d" % int(grp_id)
        try:
            rep = self.session.get(url)
            result = json.loads(rep.text)["data"]
        except Exception,e:
            log.error(str(e))
        return result




    def _create_uic_user(self,user,email,phone):
        url = "http://127.0.0.1:5050/uic/user/create"
        data = {"username":user,"email":email,"sms":phone}
        try:
            rep = self.session.post(url,data= data)
            print rep.text
        except Exception,e:
            log.error(str(e))
        return True


    def api_update_uic_user(self,user,email,phone):
    # update user info
        url = "http://127.0.0.1:5050/uic/user/info/update" 
        data = {"user": user, "cnname":"","email":email,"phone":phone}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True


    def _delete_uic_user(self, user):
    ## func delete uic user
        url = "http://127.0.0.1:5050/uic/user/info/delete"
        data = {"user": user}
        try:
            rep = self.session.post(url,data= data)
            print rep.text
        except Exception,e:
            log.error(str(e))
        return True

    def _bind_uic_user(self,user,grp_name):
        ### bind user to group
        grp_id = self._get_uic_group(grp_name)
        user_id = self._get_uic_user(user)
        url = "http://127.0.0.1:5050/uic/group/adduser/%d" % int(grp_id)
        print url
        data = {"user_id": user_id}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True

    def _unbind_uic_user(self, user,grp_name):
        ## unbind user from group
        grp_id = self._get_uic_group(grp_name)
        user_id = self._get_uic_user(user)
        url = "http://127.0.0.1:5050/uic/group/deluser/%d" % int(grp_id)
        data = {"user_id": user_id}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
        return True      

    def api_create_user(self, grp_name,user,email,phone):
        ### create user
        if not self._create_uic_user(user,email,phone):
            return None
        if not self._bind_uic_user(user,grp_name):
            return None
        return True

    def api_delete_user(self,grp_name,user):
        ### delete user
        if not self._unbind_uic_user(user,grp_name):
            return None
        if not self._delete_uic_user(user):
            return None
        return True

    def api_get_user(self,user):
        url = "http://127.0.0.1:5050/uic/user/get/id/%s" % user
        data_dict = {}
        try:
            rep = self.session.get(url)
            print rep.text
            result = json.loads(rep.text)["id"]

        except Exception,e:
            log.error(str(e))
            return None
        data_dict["id"] = result[0]
        data_dict["name"] = result[1]
        data_dict["email"] = result[2]
        data_dict["phone"] = result[3]
        return data_dict

    # def api_update_user_strategy(self, grp_name,tem_name,actions):
    # ### bind action in uic
    #     tpl_id = self._get_template_id(tem_name)
    #     data = {"uic": grp_name, "url":"","callback":"","before_callback_sms":"","before_callback_mail":"",
    #         "after_callback_sms":"","after_callback_mail":""}
    #     url = "http://127.0.0.1:5050/template/action/update/%d" % tpl_id
    #     try:
    #         rep = self.session.post(url,data= data)
    #     except Exception,e:
    #         print str(e)
    #         return None
    #     priority = self._calculate_priority(actions)
    #     url_p = "http://127.0.0.1:5050/strategy/update_action"
    #     data_p = {"tpl_id":str(tpl_id),"action":str(priority)} 
    #     try:
    #         rep = self.session.post(url_p,data=data_p)
    #     except Exception,e:
    #         print str(e)
    #         return None
    #     return True

    def api_update_user_strategy(self, grp_name,tem_name):
    ### bind action in uic
        tpl_id = self._get_template_id(tem_name)
        data = {"uic": grp_name, "url":"","callback":"","before_callback_sms":"","before_callback_mail":"",
            "after_callback_sms":"","after_callback_mail":""}
        url = "http://127.0.0.1:5050/template/action/update/%d" % tpl_id
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
            return None
        return True


    def _get_template_id(self, tem_name):
        url = "http://127.0.0.1:5050/template/get/info/%s" % tem_name
        try:
            rep = self.session.get(url)
            result = json.loads(rep.text)["data"][0]
        except Exception,e:
            log.error(str(e))
            return None
        return result['id']



    def _get_strategy_sid(self, metric,op,right_value,tpl_id):
        url = "http://127.0.0.1:5050/strategy/get/info"
        data = {"metric":metric,"op":op,"right_value":right_value,"tpl_id":tpl_id}
        try:
            rep = self.session.post(url,data=data)
            sid = json.loads(rep.text)["data"][0]
            print sid
        except Exception,e:
            log.error(str(e))
        return sid

    def _get_uic_group(self, grp_name):
        url = "http://127.0.0.1:5050/uic/group/get/id/%s" % grp_name
        try:
            rep = self.session.get(url)
            print rep.text
            id = json.loads(rep.text)["id"][0]
# Added by Caton
            log.debug('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            log.debug("Group ID is:  %s" % id)
            log.debug('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        except Exception,e:
            log.error(str(e))
            return None
        return id

    def _get_uic_user(self, user_name):
        url = "http://127.0.0.1:5050/uic/user/get/id/%s" % user_name
        try:
            rep = self.session.get(url)
            id = json.loads(rep.text)["id"]
        except Exception,e:
            log.error(str(e))
        return id  



    ## create host group
    def api_create_group(self,grp_name):
        url = "http://127.0.0.1:5050/group/create"
        data = {"grp_name": grp_name}
        try:
            rep = self.session.post(url, data=data)
        except Exception,e:
            log.error(str(e))
            return None
        return True
    ## delete host group
    def api_delete_group(self,grp_name):
        grp_id = self.api_get_group(grp_name)["grp_id"]
        url = "http://127.0.0.1:5050/group/delete/%d" % int(grp_id)
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
        return True
    ## get host group id
    def api_get_group(self,grp_name):
        url = "http://127.0.0.1:5050/group/get/%s" % grp_name
        try:
            rep = self.session.get(url)
            grp_data = json.loads(rep.text)["data"]
        except Exception,e:
            log.error(str(e))
            return None
        return grp_data
    ## create host


    def api_get_hostid(self,hostname):
        print hostname
        url = "http://127.0.0.1:5050/host/hostid"
        data = {"host":hostname}
        try:
            rep = self.session.post(url,data=data)
           # pdb.set_trace()
            print "@@@@@@@@@@@@"
            print rep.text
            print rep.status_code
        except Exception,e:
            log.error(str(e))
            return None
        else:

            if rep.status_code == 200:
	        result = json.loads(rep.text)
                print result
                return result["hostid"]
            else:
                return None

    def api_get_hostgroup(self,hostname,grp_name):
        url = "http://127.0.0.1:5050/host/hostgroup"
        grp_id = self.api_get_group(grp_name)["grp_id"]
        if not grp_id:
            return None
        host_id = self.api_get_hostid(hostname)
        print "host_id: ",host_id
        if not host_id:
            return None
        data = {"hostid":str(host_id),"grpid":str(grp_id)}
        rep = self.session.post(url,data=data)
        print "rep.text: ",rep.text
        if rep.status_code == 200:
            return True
        else:
            return None 


    #def api_get_host_fromgroup(self,hostname):
     #   host_id = self.api_get_hostid(hostname)
    def api_get_host_fromgroup(self,host_id):
        if not host_id:
            return None
        url = "http://127.0.0.1:5050/host/hostgroup/%s" % str(host_id)
        rep = self.session.get(url)
        print "!!!!!!!!!!!!222:",rep.text
        if rep.status_code == 200:
            return True
        else:
            return None



    def api_bind_host_group(self,grp_name,host):
        url = "http://127.0.0.1:5050/host/add"
        grp_id = self.api_get_group(grp_name)["grp_id"]

        data = {"group_id":grp_id,"hosts":host}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
            return None
        return True
    def api_unbind_host_group(self,grp_name,host_id):
        url = "http://127.0.0.1:5050/host/remove"
        grp_id = self.api_get_group(grp_name)["grp_id"]
        data={"grp_id":grp_id,"host_ids":host_id}
        try:
            rep = self.session.post(url,data= data)
        except Exception,e:
            log.error(str(e))
            return None
        return True

    def api_get_host_group(self,grp_name):
        group_id = self.api_get_group(grp_name)["grp_id"]
        url = "http://127.0.0.1:5050/group/%d/hosts.txt" % int(group_id)
        try:
            rep = self.session.get(url)
            result = rep.text.split("\n")
        except Exception,e:
            log.error(str(e))
            return None
        return result

    def api_bind_template_group(self,tpl_name,grp_name):
        tpl_id = self._get_template_id(tpl_name)
        grp_id = self.api_get_group(grp_name)["grp_id"]
        url = "http://127.0.0.1:5050/group/bind/template?tpl_id=%d&grp_id=%d" % (int(tpl_id),int(grp_id))
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
        return True
    def api_unbind_template_group(self,tpl_name,grp_name):
        tpl_id = self._get_template_id(tpl_name)
        grp_id = self.api_get_group(grp_name)["grp_id"]
        url = "http://127.0.0.1:5050/template/unbind/group?tpl_id=%d&grp_id=%d" % (int(tpl_id),int(grp_id))
        try:
            rep = self.session.get(url)
        except Exception,e:
            log.error(str(e))
            return None
        return True

    def api_get_host_from_template(self,tpl_name):
        tpl_id = self._get_template_id(tpl_name)
        url = "http://127.0.0.1:5050/template/bind_g/%d" % tpl_id
        try:
            rep = self.session.get(url)
            grp_name = json.loads(rep.text)["data"][0]["grp_name"]
        except Exception,e:
            log.error(str(e))
            return None
        result = self.api_get_host_group(grp_name)
        ## return list
        return result


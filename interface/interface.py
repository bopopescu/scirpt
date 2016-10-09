#!/usr/bin/python2.7
#-*- coding:utf-8 -*-
from flask import request,abort,jsonify,Flask
import pprint
import smtplib
import sys
import thread
import requests,json
from email.mime.text import MIMEText
from email.header import Header
from logger import Logger
import os
import time
import random
from xml.etree import ElementTree as Et
import config
from db import DB
from datetime import datetime as date


#url='http:'
#account=''
#passwd=''
#mail_sender = 'service@xiangcloud.com.cn'
mail_sender = 'zb_cloud2016@163.com'
#mail_smtpserver = "smtp.hostuc.net"
mail_smtpserver = "smtp.163.com"
#mail_user = 'service@xiangcloud.com.cn'
mail_user = 'zb_cloud2016@163.com'
#mail_password = 'Passw0rd4elephantcloud'
mail_password = 'xiangcloud1234'

reload(sys)
sys.setdefaultencoding('utf-8')
dirname = os.path.dirname(os.path.abspath(__file__))
log = Logger(debug=True,filename=os.path.join(dirname,"app.log"))
db_handler = DB(config.mysqldb_user, config.mysqldb_password, config.mysqldb_host, config.mysqldb_db)
tab_name = "sms"

# try:
#   smtp = smtplib.SMTP()
#   rep=smtp.connect(mail_smtpserver)
#   smtp.login(mail_user,mail_password)
#   log.debug("login stmp server success!")
# except Exception,e:
#   log.error("Err! login stmp fail!")
#   log.error("the fail text is:%s" % str(e))
#   sys.exit(2)

  



def mail(mail_body,mail_subject,mail_receiver):
  try:
    smtp = smtplib.SMTP()
    rep=smtp.connect(mail_smtpserver)
    smtp.login(mail_user,mail_password)
    log.debug("login stmp server success!")
  except Exception,e:
    log.error("Err! login stmp fail!")
    log.error("the fail text is:%s" % str(e))
    sys.exit(2)

  sid = str(time.time()).split(".")[0]+str(random.randint(100,999))
  msg = MIMEText(mail_body,_charset="utf-8")
  msg['subject']=mail_subject
  msg['From'] = mail_sender
  msg['To'] = mail_receiver
  log.debug("mail [subject]:%s;[from]:%s;[to]:%s;[body]:%s;[sid]:%s" % (mail_subject,mail_sender,mail_receiver,mail_body,sid))
  try:
    smtp.sendmail(mail_sender,mail_receiver.split(','),msg.as_string())
  except Exception,e:
    log.error("send mail to %s fail,the fail text is:%s;[sid]:%s" % (mail_receiver,str(e),sid))
    return None
  smtp.quit()
  log.debug("send mail to %s success!;[sid]:%s" % (mail_receiver,sid))
  return True

def sms(tel,content):
  db_handler = DB(config.mysqldb_user, config.mysqldb_password, config.mysqldb_host, config.mysqldb_db)
  tab_name = "sms"
  sid = str(time.time()).split(".")[0]+str(random.randint(100,999))
#  send_time = str(date.now()).split(".")[0]
  tab_para = "(sid,content,receiver,status)"
  content_new = content + "【象云科技】"
  data={'userid':'21263','account':account,'password':passwd,'content':content_new,'action':'send','mobile':tel}
  try:
    a=db_handler._insert_(tab_name, tab_para,sid,content,tel,0)
    rep = requests.post(url,data=data,timeout=60)
    result = rep.text
    flag = Et.fromstring(result).find("returnstatus").text
    flag="Success"
    if flag == "Success":
      status = 2
    else:
      status = 1
    return_time = str(date.now()).split(".")[0]
    db_handler._update_(tab_name, "status=%d" % (status), "where sid=%s" % sid)
    log.debug("send %s to %s,and return code is:%s;[sid]=%s" % (content_new,tel,result,sid))
  except Exception,e:
    log.error(str(e))
    db_handler._close_()
    return None
  db_handler._close_()
  return True



app = Flask(__name__)
@app.route('/sms',methods=['POST'])
def create_sms():
  if  request.method == 'POST':
     data=request.values.to_dict()
     tel=data['tos'].strip(",")
     if len(tel) == 0:
       return jsonify(msg="content can`t be blank"),500
     content=data['content']
     result = sms(tel,content)
     if not result:
       return jsonify(msg="fail"),500
     return jsonify(msg="success"),200

@app.route('/mail',methods=['POST'])
def create_mail():
  if request.method == 'POST':
    data=request.values.to_dict()
    email=data['tos']
    content=data['content']
    subject=data['subject']
    result = mail(content,subject,email)
    if not result:
      return jsonify(msg="fail"),500
    return jsonify(msg="success"),200

@app.route('/health')
def test():
  return "ok"

    
if __name__ == '__main__':
  app.run(host="0.0.0.0",port=5000,debug=True)


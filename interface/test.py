#-*- coding:utf-8 -*-
from db import DB
import config
db_handler = DB(config.mysqldb_user, config.mysqldb_password, config.mysqldb_host, config.mysqldb_db)
tab_name = "sms"

tab_para = "(sid,content,receiver,status)"
sid="1234521111111"
content="阿萨德发的说法阿斯蒂芬"
tel="18510255276"
#a=db_handler._insert_(tab_name, tab_para,sid,content,tel,0)
print content


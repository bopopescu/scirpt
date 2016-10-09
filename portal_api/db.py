#!/usr/bin/python2.7

import MySQLdb
import datetime
##### modified db
class DB():
    def __init__(self,user,password,host,dbname):
        self.user = user
        self.password = password
        self.host = host
        self.dbname = dbname
        self.conn = MySQLdb.connect(user=self.user, passwd=self.password,
                                    host=self.host, db=self.dbname)
        self.cursor = self.conn.cursor()

### select one record from db and return dict
    def _select_(self,tablename,sel_data,params=None):
        sql = "select %s from %s %s" % (sel_data,tablename,params)
        dict_data = {}
        n = self.cursor.execute(sql)
        if not n:
            return None
        row = self.cursor.fetchall()[0]
        for i in range(len(sel_data.split(','))):
            key = sel_data.split(',')[i]
            value = row[i]
            dict_data[key] = value
        return dict_data
### select many record from db and return dict
    def _select_many_(self,tablename,sel_data,params=None):
        sql = "select %s from %s %s" % (sel_data,tablename,params)
        list_data = []
        n = self.cursor.execute(sql)
        if not n:
            return None
        rows = self.cursor.fetchall()
        for row in rows:
            dict_data = {}
            for i in range(len(sel_data.split(','))):
                key = sel_data.split(',')[i]
                value = row[i]
                dict_data[key] = value
            list_data.append(dict_data)
        return list_data

    def _insert_(self,tab_name,tab_para, *args):
        tab_temp =  ['"%s"' % i for i in args ]
        tab_value = ','.join(tab_temp)
        #hostname,ip,type,state,update_time,create_time,user
        sql = 'insert into %s%s values(%s)' % (tab_name,tab_para,tab_value)
        try:
            n = self.cursor.execute(sql)
        except Exception,e:
            print str(e)
            self.conn.rollback()
            return None
        self.conn.commit()
        return n
    def _del_(self,tablename,params=None):
        sql = 'delete from %s %s' % (tablename,params)
        n = self.cursor.execute(sql)
        try:
            n = self.cursor.execute(sql)
        except Exception,e:
            print str(e)
            self.conn.rollback()
            return None
        self.conn.commit()
        return n
    def _update_(self,tabname,tab_value,params):
        sql = 'update %s set %s %s' % (tabname,tab_value,params)
        try:
            n = self.cursor.execute(sql)
        except Exception,e:
            print str(e)
            self.conn.rollback()
            return None
        self.conn.commit()
        return n

    def _close_(self):
        self.conn.close()
if __name__ == '__main__':
    db = DB("root","password","localhost","falcon_portal")
    tabname = "falcon_hosts"
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sel_data = "hostname,ip"
    paras = 'where hostname="test"'
    c=db._del_(tabname,'where hostname="zhang"')
    db._close_
    print c


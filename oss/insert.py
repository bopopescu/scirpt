#!/usr/bin/python2.7
from  flask import Flask,request,jsonify
import MySQLdb
import json

def InsertDB(user,password,dbname,host,sql):
    conn = MySQLdb.connect(host=host,user=user,passwd=password,db=dbname)
    cursor = conn.cursor()
    try:
        n = cursor.execute(sql)
        conn.commit()
    except Exception,e:
        conn.rollback()
        conn.close()
        return jsonify(msg=str(e))
    conn.close()
    return jsonify(msg="ok")

app = Flask(__name__)
@app.route('/addvm',methods=["POST"])
def create_vm():
    user = "root"
    password = "password"
    dbname = "falcon_portal"
    host = "127.0.0.1"
    vm_ip = request.form['ip']
    vm_host = request.form['hostname']
    sql = 'insert into host(hostname,ip) values ("%s","%s")' % (vm_host,vm_ip)
    response = InsertDB(user,password,dbname,host,sql)
    return response

if __name__ == '__main__':
    app.run(debug=True,port=5060)


/*监控虚拟机，从falcon_portal.vm_host库中读取hostname,然后根据　节点　进行分发*/
package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

//define mysql info
const (
	mysql_user     = "falcon"
	mysql_password = "password"
	mysql_db       = "falcon_portal"
	mysql_host     = "127.0.0.1"
)

//define data type
type VmData struct {
	node      string
	instances []string
}

type Data60 struct {
	hosts []*VmData
}

type Data300 struct {
	hosts []*VmData
}

// query data from table vm_host
func SelectData(interval int, node string) *VmData {
	db_info := fmt.Sprintf("%s:%s@tcp(%s:3306)/%s?charset=utf8", mysql_user, mysql_password, mysql_host, mysql_db)
	db, err := sql.Open("mysql", db_info)
	if err != nil {
		log.Println(err)
	}
	defer db.Close()
	row, err := db.Query("select hostname from vm_host where node=? and interval_time=?", node, interval)
	if err != nil {
		log.Println(err)
		return nil
	}
	var name string
	m := new(VmData)
	for row.Next() {
		row.Scan(&name)
		m.instances = append(m.instances, name)
	}
	m.node = node
	return m
}

//query nodes
func AggreNode() []string {
	db_info := fmt.Sprintf("%s:%s@tcp(%s:3306)/%s?charset=utf8", mysql_user, mysql_password, mysql_host, mysql_db)
	db, err := sql.Open("mysql", db_info)
	if err != nil {
		log.Println(err)
	}
	defer db.Close()
	row, err := db.Query("select node from vm_host group by node")
	if err != nil {
		log.Println(err)
		return nil
	}
	var sli []string
	var name string
	for row.Next() {
		row.Scan(&name)
		sli = append(sli, name)
	}
	return sli
}

//get data with 60s
func GetData60() *Data60 {
	node_list := AggreNode()
	m := new(Data60)
	for _, node := range node_list {
		k := SelectData(60, node)
		log.Println(k.instances)

		if k == nil {
			continue

		} else if k.instances == nil {
			log.Printf("%s have no instances\n", k.node)
			continue
		}
		m.hosts = append(m.hosts, k)

	}
	m.hosts = m.hosts[1:]
	return m
}

//get data with  300s
func GetData300() *Data300 {
	node_list := AggreNode()
	m := new(Data300)
	for _, node := range node_list {
		k := SelectData(300, node)
		if k == nil {
			continue
		}
		m.hosts = append(m.hosts, k)
	}
	m.hosts = m.hosts[1:]
	return m
}

//dial url interface
func InformUrl(m *VmData) {
	url := "http://" + m.node + ":9193/vm_monitor/"
//	url := "http://127.0.0.1:9193/vm_monitor/"
	b, err := json.Marshal(m.instances)
	if err != nil {
		log.Println(err)
	}
	body := bytes.NewBuffer([]byte(b))
	res, err := http.Post(url, "application/json;charset=utf-8", body)
	if err != nil {
		log.Println("ERR", err)
		os.Exit(2)

	}
	content, err := ioutil.ReadAll(res.Body)
	if err != nil {
		log.Println(err)
	}
	log.Printf("send %s to %s successful!\n", content, m.node)

}

// main 60s
func DataHandler60() {
	for {
		k := GetData60()
		for _, i := range k.hosts {
			InformUrl(i)
		}
		time.Sleep(time.Second * 10)
	}
}

//main 300s
func DataHandler300() {
	for {
		k := GetData300()
		for _, i := range k.hosts {
			InformUrl(i)
		}
		time.Sleep(time.Second * 30)
	}
}

func Main() {
	go DataHandler60()
	go DataHandler300()
}

func main() {
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	Main()
	for {
		time.Sleep(time.Second * 60)
	}
}

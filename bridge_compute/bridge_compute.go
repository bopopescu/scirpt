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
//	"os"
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
	} else if row.Err() != nil {
		log.Println("it is no data in table vm_host!!!")
		return nil
	}
	var name string
	m := new(VmData)
	for row.Next() {
		row.Scan(&name)
		if name == "" {
			return nil
		}
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
	} else if row.Err() != nil {
		log.Println("it is no node in table vm_host!!!")
		return nil
	}
	var sli []string
	var name string
	for row.Next() {
		row.Scan(&name)
		sli = append(sli, name)
	}
	log.Printf("vm_host table have nodes: %s\n", sli)
	return sli
}

//get data with 60s
func GetData60() *Data60 {
	node_list := AggreNode()
	if node_list == nil {
		return nil
	}
	m := new(Data60)
	for _, node := range node_list {
		k := SelectData(60, node)
		log.Printf("node:%s\tinstnaces:%s\n in 60s", node, k.instances)

		if k == nil {
			continue

		} else if k.instances == nil {
			log.Printf("%s have no instances with 60s\n", k.node)
			continue
		}
		m.hosts = append(m.hosts, k)

	}
	//	m.hosts = m.hosts[1:]
	log.Println("M:", m)
	return m
}

//get data with  300s
func GetData300() *Data300 {
	node_list := AggreNode()
	if node_list == nil {
		return nil
	}
	m := new(Data300)
	for _, node := range node_list {
		k := SelectData(300, node)
		log.Printf("node:%s\tinstances:%s\n in 300s", node, k.instances)
		if k == nil {
			continue
		} else if k.instances == nil {
			log.Printf("%s have no instances with 300s\n", k.node)
			continue
		}
		m.hosts = append(m.hosts, k)
	}
	//	m.hosts = m.hosts[1:]
	return m
}

//dial url interface
func InformUrl(m *VmData) {
	url := "http://" + m.node + ":9193/vm_monitor/"
	data_map := make(map[string][]string)
	//url := "http://127.0.0.1:9193/vm_monitor/"
	data_map["instances_list"] = m.instances
	b, err := json.Marshal(data_map)
	if err != nil {
		log.Println(err)
	}
	body := bytes.NewBuffer([]byte(b))
	res, err := http.Post(url, "application/json;charset=utf-8", body)
	if err != nil {
		log.Println("ERR", err)
//		os.Exit(2)
		return

	}
	content, err := ioutil.ReadAll(res.Body)
	if err != nil {
		log.Println(err)
	}
	log.Printf("send %s to %s successful!\n", b, m.node)
	log.Printf("return contend is %s\n", content)

}

// main 60s
func DataHandler60() {
	for {
		time.Sleep(time.Second * 20)
		k := GetData60()
		if k == nil {
			continue
		}
		for _, i := range k.hosts {
			log.Printf("### inform node:%s\n", i.node)
			go InformUrl(i)
		}
	}
}

//main 300s
func DataHandler300() {
	for {
		time.Sleep(time.Second * 60)
		k := GetData300()
		if k == nil {
			continue
		}
		for _, i := range k.hosts {
			go InformUrl(i)
		}
	}
}

func Main() {
	fmt.Println("程序开始．．．")
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

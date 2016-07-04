#!/usr/bin/env python 

import urllib.request
import os,time,sys
import platform
import socket
import sqlite3
import multiprocessing
from sqlite3 import *
from bs4 import BeautifulSoup
from multiprocessing import cpu_count


mac_headers = {
'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
"Connection":"keep-alive",}

static_url = 'http://www.pm25.com/city/'
id_table = 0;
location = '宁德'
city_aqi = 10
aqi = 10
pm25 = 10
pm10 = 10
updatetime = 2015


def writeSqlite(cityName):
    
    global id_table
    global location 
    global city_aqi
    global aqi
    global pm25 
    global pm10
    global updatetime 
    
    db = r"aqi.db"
    conn = sqlite3.connect(db)
    curs = conn.cursor()           #创建游标
 
    table_create ='create table if not exists '+cityName+\
    ' (id integer primary key,location varchar(10),aqi text NULL,pm25 text NULL ,pm10 text NULL,updateTime DATETIME NULL)'
    curs.execute(table_create)
    table_select = 'SELECT id, location,aqi, pm25, pm10 , updateTime  from '+cityName   
    curs = conn.execute(table_select) 

    if id_table == 0:
        table_count = 'select count(*) from '+cityName
        curs.execute(table_count)
        rows = curs.fetchone()
        id_table=rows[0];

    table_write = 'insert into '+cityName+' values (?,?,?,?,?,?)'
    curs.execute(table_write, (id_table,location,aqi,pm25,pm10,updatetime))
    id_table = id_table+1
        
    conn.commit()  #刷新
    curs.close()  #关闭游标
    conn.close()    #关闭连接

def  getAqi(cityName):

    global id_table
    global location 
    global city_aqi
    global aqi
    global pm25 
    global pm10
    global updatetime 

    url=static_url + cityName + '.html'
    # timeout in seconds
    timeout = 2
    socket.setdefaulttimeout(timeout)
    req = urllib.request.Request(url,headers=mac_headers)
    response = urllib.request.urlopen(req)
    the_page = response.read()
    response.close()

    pm = BeautifulSoup(the_page,"html.parser",from_encoding="utf-8")

    city = pm.select(".city_name")[0].get_text()

    citydata_updatetime = pm.select(".citydata_updatetime")[0].get_text();
    updatetime = citydata_updatetime[5:24]
    print(updatetime)
    location = pm.select(".city_name")[0].get_text().replace(' ','')
    print(location)
    
    for locate in pm.select(".cbo_left  div"):
        str_list=locate.select(".cbol_aqi_num ")

        for get in str_list:
            aqi = get.get_text()
    pm25 = 0
    pm10 = 0
    writeSqlite(cityName)

    for locate in pm.select(".pj_area_data ul:nth-of-type(2) li"):     
        location = locate.select(".pjadt_location")[0].get_text().rjust(15).replace(' ','')
        aqi = locate.select(".pjadt_aqi")[0].get_text().rjust(15).replace(' ','')
        pm25 = locate.select(".pjadt_pm25")[0].get_text().rjust(15)[0:10].replace(' ','') 
        pm10 = locate.select(".pjadt_pm10")[0].get_text().rjust(15)[0:10].replace(' ','') 

        print(location,'     ',aqi,'     ',pm25,'     ',pm10)
        writeSqlite(cityName)


if __name__ == '__main__':
    sysstr = platform.system()  

    print(sysstr)

    while 1:

        try:
            city_list = ["ningde","wuxi","shanghai","jinan","binzhou","beijing"]
            for city in city_list:
                id_table = 0
                try:
                    getAqi( city )
                except:
                    pass
                time.sleep(10*60)
        except:
            print("Web error")
            time.sleep(10)
            pass




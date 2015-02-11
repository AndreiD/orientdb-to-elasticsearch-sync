#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from utils.general_utils import cool_log, get_web_content, get_web_content_auth, sizeof_fmt, post_to_es, delete_in_es
import datetime
from config import Config
import json
import pyorient
import urllib
import math
import requests


#------------- PLEASE ADAPT IT TO MATCH YOUR DB. I HAVE A "User" class with a name property in orientdb.

# ------ start silly benchmark --------->>>>>>>>>>>>

client = pyorient.OrientDB(Config.ORIENTDB_SERVER_URL.replace("http://", ""), 2424)
client.db_open(Config.ORIENTDB_DB_NAME, Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD)

start_time = datetime.datetime.now()

words_to_search = ['dan', '321d12dfs', '123']


#------- benchmarking orientdb python ----------
try:
    for word in words_to_search:
        query = "SELECT FROM User WHERE name LIKE '%" + word + "%' LIMIT 500"
        res = client.command(query)
except Exception, ex:
    cool_log(ex.message, "error")

cool_log('Duration orientdb [pyorient]: ....... {}'.format(datetime.datetime.now() - start_time))



#------- benchmarking es  ----------
start_time = datetime.datetime.now()
for word in words_to_search:
    query = '{"query": {    "wildcard": {       "name": {          "value": "*' + word + '*"       }    }}}'
    try:
        m_req = requests.post(Config.ES_SERVER_URL + ":" + Config.ES_SERVER_PORT + "/" + Config.ORIENTDB_DB_NAME.lower()+ "/user/_search", data=query, timeout=5)
    except requests.exceptions.RequestException as e:
        cool_log(e, category="error")

cool_log('Duration ES REST API: ............... {}'.format(datetime.datetime.now() - start_time))
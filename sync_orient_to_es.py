#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from utils.general_utils import cool_log, get_web_content, get_web_content_auth, sizeof_fmt, post_to_es, delete_in_es
import datetime
from config import Config
import json
import pyorient
import urllib


BASE_URL_ORIENTDB = Config.ORIENTDB_SERVER_URL + ":" + Config.ORIENTDB_SERVER_PORT
BASE_URL_ES = Config.ES_SERVER_URL + ":" + Config.ES_SERVER_PORT
show_verbose = False


def mlogger(message, category="info"):
    if show_verbose:
        cool_log(message, category)


def initialize():
    global client, classes_to_es, json_content, Classes, mClass, superClass
    # ---- check elastic search server is working
    if json.loads(get_web_content(BASE_URL_ES))['status'] == 200:
        mlogger("ES SERVER............... Connected OK")
    else:
        mlogger("ES SERVER......... FAILED. Check config ?", category="error")
        sys.exit(1)

    # ---- check orientdb server is working
    if Config.ORIENTDB_DB_NAME in json.loads(get_web_content_auth(BASE_URL_ORIENTDB + "/listDatabases", Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD))['databases']:
        mlogger("ORIENTDB SERVER......... Connected OK")
    else:
        mlogger("ORIENTDB SERVER......... FAILED. Check config ?", category="error")
        sys.exit(1)

    client = pyorient.OrientDB(Config.ORIENTDB_SERVER_URL.replace("http://", ""), 2424)
    client.db_open(Config.ORIENTDB_DB_NAME, Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD)
    mlogger(Config.ORIENTDB_DB_NAME + ".......... size: " + str(sizeof_fmt(client.db_size())) + " | records: " + str(client.db_count_records()))
    # ----------- getting all the classes V and E
    classes_to_es = []
    json_content = json.loads(get_web_content_auth(BASE_URL_ORIENTDB + "/database/" + Config.ORIENTDB_DB_NAME, Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD))
    Classes = json_content['classes']
    for mClass in Classes:
        superClass = mClass['superClass']
        if superClass == "V":
            classes_to_es.append(mClass['name'])
    mlogger("Classes to ElasticSearch >> " + str(classes_to_es))
    mlogger(" ")


def main():
    start_time = datetime.datetime.now()
    initialize()

    mlogger("----------- SYNC FROM ORIENTDB TO ELASTICSEARCH ------------------")
    for xClass in classes_to_es:
        total_records_orientdb = client.query("SELECT COUNT(*) as total_rec FROM " + str(xClass))[0].total_rec - 1
        mlogger("Total records [" + xClass + "] >> " + str(total_records_orientdb))

        for index in range(0, total_records_orientdb):

            if index != 0 and index % 1000 == 0:
                mlogger("completed...." + str(index) + " records")

            orientdb_res = get_web_content_auth(BASE_URL_ORIENTDB + "/documentbyclass/" + Config.ORIENTDB_DB_NAME + "/" + xClass + "/" + str(index), Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD)
            rid = json.loads(orientdb_res)['@rid']
            base_es_record_url = BASE_URL_ES + "/" + Config.ORIENTDB_DB_NAME.lower() + "/" + xClass.lower() + "/" + urllib.quote_plus(str(rid))

            es_stored_record = get_web_content(base_es_record_url)
            if '"found":false' in es_stored_record or '"status":404' in es_stored_record:
                post_to_es(base_es_record_url, orientdb_res)
            else:
                if json.loads(orientdb_res) != json.loads(es_stored_record)['_source']:
                    post_to_es(base_es_record_url, orientdb_res)

    mlogger("----------- SYNC FROM ELASTICSEARCH TO ORIENTDB ------------------")
    for xClass in classes_to_es:
        xfrom = 0
        total_hits = 1000
        while xfrom < total_hits:

            json_es_indexes = json.loads(get_web_content(BASE_URL_ES + "/" + Config.ORIENTDB_DB_NAME.lower() + "/" + xClass.lower() + "/" + "_search?pretty=true&fields=&size=1000&from=" + str(xfrom)))

            total_hits = json_es_indexes['hits']['total']

            if xfrom != 1000 and xfrom % 1000 == 0:
                mlogger("completed...." + str(xfrom) + " records")

            xfrom = xfrom + 1000

            for mRecord in json_es_indexes['hits']['hits']:
                rid = mRecord['_id']
                try:
                    content_orient = get_web_content_auth(BASE_URL_ORIENTDB + "/query/" + Config.ORIENTDB_DB_NAME + "/sql/" + urllib.quote_plus("SELECT FROM " + rid), Config.ORIENTDB_USER, Config.ORIENTDB_PASSWORD)
                    es_content = get_web_content(BASE_URL_ES + "/" + Config.ORIENTDB_DB_NAME.lower() + "/" + xClass.lower() + "/" + urllib.quote_plus(str(rid)))

                    if len(json.loads(content_orient)['result']) < 1:
                        delete_in_es(es_content)

                except Exception, ex:
                    delete_in_es(BASE_URL_ES + "/" + Config.ORIENTDB_DB_NAME.lower() + "/" + xClass.lower() + "/" + urllib.quote_plus(str(rid)))
                    pass

    client.db_close()

    mlogger('Duration: {}'.format(datetime.datetime.now() - start_time))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-v":
            show_verbose = True
    main()

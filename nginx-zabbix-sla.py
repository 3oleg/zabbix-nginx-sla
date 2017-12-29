#!/usr/bin/env python3
# 3oleg@mail.ru

# чтобы работало, надо python3-pycurl и zabbix-sender, остальное по умолчанию должно быть
# apt install python3-pycurl zabbix-sender

import re
import os
import sys
import subprocess
from curl import Curl

# Single config
URL = 'http://127.0.0.1:6666/sla_status'


def get(url):
    c = Curl()
    res = c.get(url)
    c.close()
    return (res.decode())


def filterkey(i):
    # "\, ', ", `, *, ?, [, ], {, }, ~, $, !, &, ;, (, ), <, >, |, #, @, 0x0a" a - not allowed in key
    # мы не можем использовать проценты в ключах
    # договоримся так: все что < 100 - персентиль
    i = re.sub('/', '-', i)
    i = re.sub(':', '-', i)
    return re.sub('[^A-Za-z0-9-\._]+', '', i)


def runcommand(command):
    res = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, )
    return map(lambda x: x.decode('utf-8'), res.communicate())


def sla_json():
    bad = ['avg', 'mov', 'agg']
    json = {}
    res = get(URL)
    # получаем json из запроса
    for i in res.split('\n'):
        data = i.split('.')
        if len(data) < 3:
            continue
        data = i.split('.')
        # I twist the top I cheat, I want to
        key, value = data[-1].split(' = ')
        if 'time' in data[-3]:
            upstream = '.'.join(data[1:-3])
            key = '.'.join([data[-3], data[-2], key])
        elif data[-2] in bad or key in bad:
            upstream = '.'.join(data[1:-2])
            key = '.'.join([data[-2], key])
        else:
            upstream = '.'.join(data[1:-1])

        if not upstream in json:
            json[upstream] = {}
        json[upstream][key] = int(value)
    return json


def zabbixsend(data):
    command = 'echo "%s" | zabbix_sender  -vv -c /etc/zabbix/zabbix_agentd.conf -s \'%s\' -i - ' % (data, os.uname()[1])
    # print(command)
    out, err = runcommand(command)
    # print(out,err)


def discovery():
    t = []
    for i in sla_json():
        key = filterkey(i)
        t.append('{"{#UPSTREAM}": "%s"}' % key)
    template = '{"data":[' + ','.join(t) + ']}'
    return template


if __name__ == "__main__":
    print(discovery())
    json = sla_json()
    data = []
    for i in sys.argv[1:]:
        for upstream in json:
            data.append('- %s[%s] %i' % (filterkey(i), filterkey(upstream), json[upstream][i]))

    zabbixsend('\n'.join(data))

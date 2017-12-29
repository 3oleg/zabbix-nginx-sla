Если у вас nginx скомпилен с модулем nginx-sla (https://github.com/goldenclone/nginx-sla) 
то вы можете воспользоваться этим шаблоном мониторинга.

Шаблон использует zabbix sender, он должен быть установлен. Так же возможно отсутствует библиотека python3-pycurl
`apt install python3-pycurl zabbix-sender`

Installations:
1. Make sure that you have a SLA module in nginx `nginx -V 2>&1|grep -o 'sla'`
1. Put `nginx-zabbix-sla.py` to /opt/zabbix/
1. Put `sla.conf` to /etc/nginx/conf.d/
1. Put `zabbix-agent-nginxsla.conf` to /etc/zabbix/zabbix_agentd.d/
1. Test on zabbix server `zabbix_get -s $host_ip -k slaupstreams["50% 90% 99% 100 200 300 500 1000 2000 10000 http_2xx http_5xx"]` this 
must return json like a `{"data":[{"{#UPSTREAM}": "all"},{"{#UPSTREAM}": "unix--tmp-php.sock"}]}`
1. Import template `Template nginx-sla.xml` and pin it ho nginx host


Debug:
1. Uncomment `# print(out,err)` in `def zabbixsend`. Warning: monitoring will break after uncommenting,
but you will see additional information.
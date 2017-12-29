Если у вас nginx скомпилен с модулем nginx-sla (https://github.com/goldenclone/nginx-sla) 
то вы можете воспользоваться этим шаблоном мониторинга.

Шаблон использует zabbix sender, он должен быть установлен. Так же возможно отсутствует библиотека python3-pycurl


Installations:
1. Make sure that you have a SLA module in nginx `nginx -V 2>&1|grep -o 'sla'`
1. `apt install python3-pycurl zabbix-sender`
1. Put `nginx-zabbix-sla.py` to /opt/zabbix/
1. Put `sla.conf` to /etc/nginx/conf.d/
1. Put `zabbix-agent-nginxsla.conf` to /etc/zabbix/zabbix_agentd.d/
1. Test on zabbix server `zabbix_get -s $host_ip -k slaupstreams["50% 90% 99% 100 200 300 500 1000 2000 10000 http_2xx http_5xx"]` this 
must return json like this: `{"data":[{"{#UPSTREAM}": "all"},{"{#UPSTREAM}": "unix--tmp-php.sock"}]}`
1. Import template `Template nginx-sla.xml` and pin it ho nginx host


Debug:
1. Uncomment `# print(out,err)` in `def zabbixsend`. Warning: monitoring will break after uncommenting,
but you will see additional information.


Работает это так: Discovery каждую минуту дергает скрипт, который кроме того, что формирует json еще и отправлает аггрегированные данные на zabbix. 
В итоге мы убиваем трех зайцев: 
1. сокращаем десятки, а может и сотни запросов к nginx/sla_status до одного (если бы это были обычные или активные проверки zabbix)
1. автоматически обнаруживаем апстримы и начинаем их мониторить
1. получаем все необходимые данные за один вызов

Можно мониторить любой другой пареметр вывода nginx/sla_status: просто добавляем его в ключ slaupstreams и создаем дополнительный Item prototype копированием имеющегося.
Тут нужно обратить внимание, что в названии апстрима символы `/` и `:` заменяются `-`, а остальные не [^A-Za-z0-9-\._] удаляются. т.к. заббикс не разрешает использовать их в назвачиях ключей

Ссылки по теме: 

Идея использования zabbix_send вязта тут https://serveradmin.ru/monitoring-web-servera-nginx-i-php-fpm-v-zabbix/ Я взял их шаблон и расширил своим, что и вам советую.

Наш сайт: https://unixadm.info/
 
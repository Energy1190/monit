FROM alpine

RUN apk -U add monit python3 lm_sensors dmidecode smartmontools

RUN pip3 install docker-py \
    && pip3 install Jinja2 \
    && pip3 install plumbum \
    && pip3 install python-etcd \
    && pip3 install requests \
	&& pip3 install psutil
    
RUN awk '{print "#"$0}' /etc/monitrc >> /etc/monitrc.tmp \
    && mv /etc/monitrc.tmp /etc/monitrc \
	&& echo "include /etc/monit.d/*" >> /etc/monitrc \
	&& echo "include /etc/monit.gen/*" >> /etc/monitrc \
	&& chmod 0700 /etc/monitrc \
	&& mkdir -p /app
    
ADD . /app

VOLUME /templates
VOLUME /etc/monit.d
VOLUME /etc/monit.gen

EXPOSE 2812

RUN chmod +x /app/init.sh

CMD ["/app/init.sh"]


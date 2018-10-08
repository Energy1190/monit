FROM alpine

RUN apk -U add monit python3 lm_sensors dmidecode smartmontools

RUN pip3 install docker-py \
    && pip3 install Jinja2 \
    && pip3 install plumbum \
    && pip3 install python-etcd \
    && pip3 install requests
    
RUN awk '{print "#"$0}' /etc/monitrc >> /etc/monitrc.tmp \
    && mv /etc/monitrc.tmp /etc/monitrc
    
RUN echo "include /etc/monit.d/*" >> /etc/monitrc
RUN echo "include /etc/monit.gen/*" >> /etc/monitrc
RUN chmod 0700 /etc/monitrc \
    && mkdir -p /app

ADD . /app

VOLUME /templates
VOLUME /etc/monit.d
VOLUME /etc/monit.gen

EXPOSE 2812

CMD ["./app/init.sh"]


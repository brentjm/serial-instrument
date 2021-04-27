#FROM python:3.7
FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 mosquitto\
    && adduser -S -h /home/mosquitto -s /bin/sh -u 1001 -g 1001 mosquitto\
    && pip install paho-mqtt PyYAML coloredlogs

USER mosquitto
RUN mkdir -p /home/mosquitto/python/socket-mqtt
COPY --chown=mosquitto:mosquitto socket_mqtt.py logger_conf.yml /home/mosquitto/python/socket-mqtt/
WORKDIR /home/mosquitto/python/socket-mqtt

ENTRYPOINT ["python", "-m", "socket_mqtt"]
#CMD ["--socket_host", "fake", "--socket_port", "54132", "--mqtt_broker", "192.168.1.3", "--group_id", "prototype", "--device_id", "fake"]

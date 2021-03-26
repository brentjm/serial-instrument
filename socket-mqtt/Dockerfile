FROM python:3.7
#FROM arm32v6/python:3.7

RUN addgroup --system --gid 1001 mosquitto\
    && adduser --system --home /home/mosquitto --shell /bin/sh --uid 1001 --gid 1001 mosquitto\
    && pip install paho-mqtt PyYAML coloredlogs

USER mosquitto
RUN mkdir -p /home/mosquitto/python/socket-mqtt
COPY --chown=mosquitto:mosquitto socket_mqtt.py logger_conf.yml /home/mosquitto/python/socket-mqtt/
WORKDIR /home/mosquitto/python/socket-mqtt

ENTRYPOINT ["python", "-m", "socket_mqtt"]
CMD ["--socket_host", "fake", "--socket_port", "54132", "--mqtt_broker", "192.168.1.3", "--client_id", "fake12"]

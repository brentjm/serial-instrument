FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 mosquitto\
    && adduser -S -h /home/mosquitto -s /bin/sh -u 1001 -g 1001 mosquitto\
    && pip install paho-mqtt PyYAML coloredlogs

USER mosquitto
RUN mkdir -p /home/mosquitto/python/socket-mqtt
COPY --chown=mosquitto:mosquitto ./socket-mqtt/ /home/mosquitto/python/
WORKDIR /home/mosquitto/python/socket-mqtt

CMD ["/bin/sh", "-c", "sleep 1000000000"]
#ENTRYPOINT ["python", "-m", "mosquitto.instrument"]
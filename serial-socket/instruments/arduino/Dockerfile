#FROM python:3.7-buster
FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 instrument\
    && adduser -S -h /home/instrument -s /bin/sh -u 1001 -g 1001 instrument\
    && pip install pyserial PyYAML coloredlogs\ 
    && sed -i -e /dialout/s/$/,instrument/ /etc/group

USER instrument
RUN mkdir -p /home/instrument/python/serial-socket
COPY --chown=instrument:instrument ./instruments/ /home/instrument/python/serial-socket/.
WORKDIR /home/instrument/python/serial-socket

ARG HOST
#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "arduino.dlc"]

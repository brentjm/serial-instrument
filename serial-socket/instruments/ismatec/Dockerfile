FROM python:3.7-buster
#FROM arm32v6/python:3.7-buster

RUN adduser --system --home /home/instrument --shell /bin/sh --uid 1001 --group instrument\
    && pip install --upgrade pip\
    && pip install pyserial PyYAML coloredlogs numpy scipy\
    && sed -i -e /dialout/s/$/,instrument/ /etc/group

USER instrument
RUN mkdir -p /home/instrument/python/serial-socket
COPY --chown=instrument:instrument ./instruments/ /home/instrument/python/serial-socket/.
WORKDIR /home/instrument/python/serial-socket

ARG HOST
#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "arduino.dlc"]

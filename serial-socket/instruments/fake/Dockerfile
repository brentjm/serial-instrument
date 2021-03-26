FROM python:3.7
#FROM arm32v6/python:3.7-alpine3.11

RUN addgroup --system --gid 1001 instrument\
    && adduser --system --home /home/instrument --shell /bin/sh --uid 1001 --gid 1001 instrument\
    && pip install PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/,instrument/ /etc/group

USER instrument
RUN mkdir -p /home/instrument/python/serial-socket
COPY --chown=instrument:instrument instruments /home/instrument/python/serial-socket/
WORKDIR /home/instrument/python/serial-socket

#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "fake.fake", "--instrument_port", "/dev/ttyUSB0", "--socket_ip", "0.0.0.0", "--socket_port", "54132"]

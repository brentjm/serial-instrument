FROM python:3.7-alpine3.11
#FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 instrument\
    && adduser -S -h /home/instrument -s /bin/sh -u 1001 -g 1001 instrument\
    && pip install PyYAML coloredlogs

USER instrument
RUN mkdir -p /home/instrument/python/test-client
COPY --chown=instrument:instrument ./serial-socket/test-client/test-client.py /home/instrument/python/test-client/.
WORKDIR /home/instrument/python/test-client

#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "test-client", "--socket_ip", "fake", "--socket_port", "5007"]

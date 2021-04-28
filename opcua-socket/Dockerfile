FROM python:3.7

RUN addgroup --system --gid 1001 python\
    && adduser --system --home /home/python --shell /bin/sh --uid 1001 --gid 1001 python\
    && pip install PyYAML coloredlogs opcua cryptography numpy

USER python
RUN mkdir -p /home/python/opc-socket
COPY --chown=python:python opc_socket.py opc_tags.py logger_conf.yml /home/python/opc-socket/
WORKDIR /home/python/opc-socket

ENTRYPOINT ["python", "-m", "opc_socket"]
CMD ["--socket_ip", "socket", "--socket_port", "54756", "--endpoint", "opc.tcp://opc-server:4840/deltavopcua/server/"]

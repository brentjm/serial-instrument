FROM python:3.7

RUN addgroup --system --gid 1001 python\
    && adduser --system --home /home/python --shell /bin/sh --uid 1001 --gid 1001 python\
    && pip install PyYAML coloredlogs opcua cryptography

USER python
RUN mkdir -p /home/python/opc-server
COPY --chown=python:python opc_server.py opc_tags.py logger_conf.yml /home/python/opc-server/
WORKDIR /home/python/opc-server

ENTRYPOINT ["python", "-m", "opc_server"]
CMD ["--endpoint", "opc.tcp://0.0.0.0:4840/deltavopcua/server/"]

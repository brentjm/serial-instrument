FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 bronkhorst\
    && adduser -S -h /home/bronkhorst -s /bin/sh -u 1001 -g 1001 bronkhorst\
    && pip install bronkhorst-propar PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/,bronkhorst/ /etc/group

USER bronkhorst
RUN mkdir -p /home/bronkhorst/python/serial-socket
COPY --chown=bronkhorst:bronkhorst ./serial-socket/ /home/bronkhorst/python/serial-socket
WORKDIR /home/bronkhorst/python/serial-socket/instruments

CMD ["/bin/sh", "-c", "sleep 1000000000"]
#ENTRYPOINT ["python", "-m", "bronkhorst.bronkhorst"]

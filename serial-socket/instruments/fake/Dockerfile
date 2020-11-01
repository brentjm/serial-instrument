FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 fake\
    && adduser -S -h /home/fake -s /bin/sh -u 1001 -g 1001 fake\
    && pip install PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/,fake/ /etc/group

USER fake
RUN mkdir -p /home/fake/python/serial-socket
COPY --chown=fake:fake ./serial-socket/ /home/fake/python/serial-socket
WORKDIR /home/fake/python/serial-socket/instruments

#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "fake.fake"]

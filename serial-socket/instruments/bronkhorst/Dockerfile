FROM arm32v6/python:3.7-alpine3.11

RUN addgroup -S -g 1001 bronkhorst\
    && adduser -S -h /home/bronkhorst -s /bin/sh -u 1001 -g 1001 bronkhorst\
    && pip install bronkhorst-propar PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/,bronkhorst/ /etc/group

USER bronkhorst
RUN mkdir /home/bronkhorst/python
COPY --chown=bronkhorst:bronkhorst ./serial-socket/ /home/bronkhorst/python
#COPY --chown=bronkhorst:bronkhorst ./serial-socket/socket/ /home/bronkhorst/python
#COPY --chown=bronkhorst:bronkhorst ./serial-socket/instruments/bronkhorst/bronkhorst.py /home/bronkhorst/python/
WORKDIR /home/bronkhorst/python

#CMD ["/bin/sh", "-c", "sleep 1000000000"]
#python -m instruments.bronkhorst.bronkhorst
#ENTRYPOINT ["python", "--version"]
#ENTRYPOINT ["python", "./instruments/bronkhorst/bronkhorst.py"]
ENTRYPOINT ["python", "-m", "instruments.bronkhorst.bronkhorst"]
#CMD ["-m" "instruments.bronkhorst.bronkhorst"]

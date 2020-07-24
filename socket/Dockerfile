FROM python:3.6

RUN useradd --create-home --home /home/bronkhorst --shell /bin/bash --uid 1000 --user-group bronkhorst\
    && pip install bronkhorst-propar PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/bronkhorst/ /etc/group

USER bronkhorst
RUN mkdir /home/bronkhorst/socket
COPY --chown=bronkhorst:bronkhorst socket_server.py libserver.py serial_instrument.py bronkhorst.py logger_conf.yml /home/bronkhorst/socket/
WORKDIR /home/bronkhorst/socket

CMD ["/bin/bash", "-c", "sleep 1000000000"]
#CMD ["python", "bronkhorst.py"]

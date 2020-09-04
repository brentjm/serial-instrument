FROM python:3.6

RUN useradd --create-home --home /home/bronkhorst --shell /bin/bash --uid 1000 --user-group bronkhorst\
    && pip install bronkhorst-propar PyYAML coloredlogs\
    && sed -i -e /dialout/s/$/bronkhorst/ /etc/group

USER bronkhorst
RUN mkdir /home/bronkhorst/python
COPY --chown=bronkhorst:bronkhorst ./serial-socket/socket/ /home/bronkhorst/python
COPY --chown=bronkhorst:bronkhorst ./serial-socket/instruments/bronkhorst/bronkhorst.py /home/bronkhorst/python/
WORKDIR /home/bronkhorst/python

#CMD ["/bin/bash", "-c", "sleep 1000000000"]
CMD ["python", "bronkhorst.py"]

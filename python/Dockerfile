FROM python:3.6

RUN useradd --create-home --home /home/bronkhorst --shell /bin/bash --uid 1000 --user-group bronkhorst\
    && pip install propar PyYAML coloredlogs

USER bronkhorst

CMD ["/bin/bash", "-c", "sleep 1000000000"]


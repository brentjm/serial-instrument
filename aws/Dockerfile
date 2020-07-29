FROM python:3.6

RUN useradd --create-home --home /home/aws --shell /bin/bash --uid 1000 --user-group aws

USER aws
RUN pip install AWSIoTPythonSDK bronkhorst-propar PyYAML coloredlogs

COPY --chown=aws:aws python/mqtt_client.py python/connection_info.json /home/aws/python/
#RUN chmod +x /home/aws/python/mqtt_client.py
WORKDIR /home/aws/python
CMD ["/bin/bash", "-c", "sleep 10000"]
#CMD ["python", "mqtt_client.py"] 
CMD ["/bin/bash", "-c", "sleep 1000000000"]


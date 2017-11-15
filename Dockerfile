FROM ubuntu:16.04

# Install dependencies
RUN apt-get update -y
RUN apt-get install -y python-pip
RUN pip install awscli --upgrade --user
RUN pip install boto3 --upgrade --user
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
RUN pip install --upgrade flask
RUN pip install --upgrade requests

ADD download.py download.py
ADD calc.py calc.py

CMD ["/usr/bin/python","download.py"]

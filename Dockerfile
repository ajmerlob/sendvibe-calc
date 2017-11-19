FROM ubuntu:16.04

# Install dependencies
RUN apt-get update -y
RUN apt-get install python-pip -y
RUN pip install awscli --upgrade --user
RUN pip install boto3 --upgrade --user 
RUN apt-get install python-pandas -y 
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
RUN pip install --upgrade flask
RUN pip install --upgrade requests
RUN pip install -U nltk

ADD download.py download.py
ADD calc.py calc.py
ADD enronsolved.csv enronsolved.csv

CMD ["/usr/bin/python","download.py"]

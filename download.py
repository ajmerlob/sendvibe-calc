import math
import sys
import os
import boto3
import json
import time
import logging

## Google authentication flow
import googleapiclient.discovery
import google_auth_oauthlib.flow
import google.oauth2.credentials

## Gmail build
import base64
import email
from apiclient import errors
from apiclient.discovery import build

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

class Download:
  
  ## Get the timestamp from the queue, which will act as the queue name to read the ids
  
  def timestamp_mod(self,ts):
    return ts.replace(":","-").replace(".","-").replace("+","-")
 
  def get_from_s3(self,key, folder):
    logging.error("s3 connection") 
    self.s3.meta.client.download_file(Bucket='email-data-full',Key=key,Filename="{}/{}".format(folder,key))


  def __init__(self):
    #print 'starting init'
    logging.error('starting init')
    self.sqs = boto3.client('sqs',region_name='us-west-2')
    self.s3 = boto3.resource('s3')
    self.data_folder = "./data"
    if not os.path.exists(self.data_folder):
      os.mkdir(self.data_folder)

    ## Open SQS and grab the queue name (which is the modded timestamp + _calc)
    logging.error('getting timestamp')
    self.MainQueueUrl = "https://sqs.us-west-2.amazonaws.com/985724320380/email_analysis" 
    main_message = self.sqs.receive_message(QueueUrl=self.MainQueueUrl,MaxNumberOfMessages=1,WaitTimeSeconds=20)
    self.rh = main_message['Messages'][0]['ReceiptHandle']
    self.sqs.delete_message(QueueUrl=self.MainQueueUrl,ReceiptHandle=self.rh)
    
    ## Set variables from the SQS message body
    self.email_address = json.loads(main_message['Messages'][0]['Body'])['email_address']
    logging.error(self.email_address)
    queue_name = json.loads(main_message['Messages'][0]['Body'])['name']
    self.AnalysisQueueUrl = "https://sqs.us-west-2.amazonaws.com/985724320380/" + queue_name

  def attempt_read_queue(self):
    for attempt in range(3):
      try:
        list_of_keys = self.sqs.receive_message(QueueUrl=self.AnalysisQueueUrl,MaxNumberOfMessages=10,WaitTimeSeconds=20)
        assert 'Messages' in list_of_keys, "Queue with S3 keys was empty or returned nothing after 20 seconds - attempt {}".format(attempt+1)
        return list_of_keys
      except AssertionError, ae:
        #print ae
        logging.error(ae)
    return None
    

  def read_queue(self):
    ## Use the SQS queue with the s3 keys
    logging.error('reading queue of ids')
    list_of_keys= self.attempt_read_queue() 
    assert list_of_keys is not None, "Queue deemed empty"

    logging.error( 'starting key reads')
    for key in list_of_keys['Messages']:
      self.get_from_s3(key['Body'],self.data_folder)
      ## After each batch of messages, delete the message and sleep as needed
      self.sqs.delete_message(QueueUrl=self.AnalysisQueueUrl  ,ReceiptHandle=key['ReceiptHandle'])

  def analyze(self):
    self.sqs.delete_queue(QueueUrl=self.AnalysisQueueUrl)
    logging.error("deleted list with s3 keys (even if it had messages in it)")
    for filename in os.listdir(self.data_folder):
      logging.error(filename + " was awesome")
    

d = Download()    
try:
  while True:
    logging.error('starting calc')
    d.read_queue()
except AssertionError, e:
  #print e
  logging.error( e)
finally:
  d.analyze()
  import calc

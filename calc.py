import math
import os
import sys
import json

import base64
import email
import smtplib

import re
import operator
import logging

#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

import pandas as pd
import numpy as np
from scipy import stats

class Solver:
    def __init__(self):
        self.df = pd.read_csv('./enronsolved.csv',sep=',',header=0,index_col=0)
        self.good_words = [c for c in self.df.columns if 'idf' not in c and 'count' not in c]

    def get_percentile(self,word,idf):
        return stats.percentileofscore(self.df[word+"_idf"].sort_values(),idf)


class Send:
  def __init__(self):
    self.address=os.environ['SENDING_ADDRESS']
    self.password = os.environ['PASSWORD']
    self.email = os.environ['TO_ADDRESS']

  def send(self, words):

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(self.address, self.password)

    message = "From: %s\r\nSubject: %s\r\nTo: %s\r\n\r\n" % (self.address,"Hello From SendVibe!",self.email) + \
"Hey there!\n\nThanks for choosing to use SendVibe!!\n\nWe are busy at work analyzing the patterns in your emails, and we thought it would be fun to send you a word count!  Below are some of the top words used in emails and how many of them are in your mailbox!\n\n{}\n\nBye for now!\n\nSendVibe <https://sendvibe.email>".format(words)
   
    ## Send that sucker out
    s.sendmail(self.address,self.email,message)
    s.sendmail(self.address,self.address,message)

    # setup the parameters of the message
#    msg = MIMEMultipart()       # create a message
#    msg['From']=self.address
#    msg['To']=self.email
#    msg['Subject']="Welcome to SendVibe!"
#
#    # add in the message body
#    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
#    del msg
    s.quit()


class Calc:
  def __init__(self):
    self.data_folder = "./data"
    self.words = {}
    self.stopwords =set(['\n',''])

  def interpret(self,message):
    msg_str = base64.urlsafe_b64decode(message.encode('ASCII'))
#    mime_msg = email.message_from_string(msg_str)
    return msg_str


  ## ['payload']['headers'] is the metadata
  ## ['payload']['parts'] contains the data
  def analyze(self):
    count = 0
    sent_count = 0
    for filename in os.listdir(self.data_folder):
      with open(self.data_folder +'/'+filename,'r') as infile:
        for line in infile:
          j = json.loads(line.strip())
          if 'payload' not in j:
            continue
          if 'labelIds' not in j:
            logging.error('labelIds not in email')
            count += 1
            continue
          if 'SENT' not in j['labelIds']:
            logging.error(j['labelIds'])
            count +=1
            continue
          count += 1
          if 'parts' in j['payload']:
            payload = j['payload']['parts']
          else:
            payload = [j['payload']]
          for part in payload:
            if part['mimeType'] == 'text/plain':
              if 'data' not in part['body']:
                logging.error("no data in the body...")
                logging.error(part['body'])
                msg = ""
              else:
                msg = self.interpret(part['body']['data'])
              msg_clean = re.sub('[!@#$\.:,@\[\]]', '', msg).lower()
              msg_split = msg_clean.strip().split(" ")
              for word in msg_split:
                if word in self.stopwords:
                  continue
                if word not in self.words:
                  self.words[word] = 0
                self.words[word] += 1
              sent_count += 1
                #print word, self.words[word]
    print count, sent_count
    return self.words

so = Solver()
c = Calc()
word_dict = c.analyze()

top_words = {}
for word in so.good_words:
  if word not in word_dict:
    top_words[word] = 0
  else:
    top_words[word] = word_dict[word]

total_count = 0.0
for word in top_words:
  total_count += top_words[word]

word_dict = {}
for word in top_words:
  word_dict[word] = so.get_percentile(word, top_words[word]/ max(total_count,1.0))

words = "\n".join(["{} - {} percentile for occurrences".format(k,int(word_dict[k]*100)/100.0) for k in word_dict])

try:
  s = Send()
  logging.error(words)
  s.send(words)
except Exception, e:
  logging.error("send didn't work")
  logging.error(e)
  raise e

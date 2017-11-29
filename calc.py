import math
import os
import sys
import json

import base64
import email
from utilities import util

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
        #print stats.percentileofscore(self.df[word+"_idf"].sort_values(),idf)
        return stats.percentileofscore(self.df[word+"_idf"].sort_values(),idf)


class Send:
  def __init__(self):
    self.address=os.environ['SENDING_ADDRESS']
    self.password = os.environ['PASSWORD']
    self.email = os.environ['TO_ADDRESS']
    self.util = Util()

  def send(self, words):
    ps,woulda,me_you,knowit,will = words
    # set up the SMTP server

    message = ("From: %s\r\nSubject: %s\r\nTo: %s\r\n\r\n" % (self.address,"Hello From SendVibe!",self.email) + \
"Hey there!\n\nThanks for choosing to use SendVibe!!\n\nWe are busy at work analyzing the patterns in your emails.  In the meantime, here are some trends that we have spotted already in the way you use some of the most common words that appear in emails:\n\n" + \
"Mind Your Ps and TYs:\n{}\n\n" + \
"Woulda, Coulda, Shoulda:\n{}\n\n" + \
"Me & You:\n{}\n\n" + \
"Support or Know-it-all:\n{}\n\n" + \
"When There's a Will:\n{}\n\n" + \
"Bye for now!\n\nSendVibe\n<https://sendvibe.email>").format(ps,woulda,me_you,knowit,will)
    print message
   
    ## Send that sucker out
    self.util.mail(self.address,self.email,message,self.password)
    self.util.mail(self.address,self.address,message,self.password)


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
            #logging.error(j['labelIds'])
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
  word_dict[word] = so.get_percentile(word, top_words[word]/total_count)

print word_dict

ps_qs = [(word_dict[word],word) for word in ['please','thank','thanks']]
woulda = [(word_dict[word],word) for word in ['would','could','should']]
me_you = [(word_dict[word],word) for word in ["i","me","you","we"]]
knowit = [(word_dict[word],word) for word in ["know",'sure','help','support','think']]
will  = [(word_dict[word],word) for word in ['will','can','need']]

def sentencify(word,counts):
  sentence = "%s: You were in the %.0f percentile for sent emails"
  return sentence % (word,counts[word])


knowit.sort()
me_you.sort()
knowit.sort()
will.sort()
words = (
"\n".join([sentencify(v,word_dict) for k,v in ps_qs]),
"\n".join([sentencify(v,word_dict) for k,v in woulda]),
"\n".join([sentencify(v,word_dict) for k,v in me_you]),
"\n".join([sentencify(v,word_dict) for k,v in knowit]),
"\n".join([sentencify(v,word_dict) for k,v in will]))

try:
  s = Send()
  logging.error(words)
  s.send(words)
except Exception, e:
  logging.error("send didn't work")
  logging.error(e)
  raise e

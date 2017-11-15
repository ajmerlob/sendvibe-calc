import math
import os
import sys
import json

import base64
import email
import smtplib

import re
import operator

#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

class Send:
  def __init__(self):
    self.address=os.environ['SENDING_ADDRESS']
    self.password = os.environ['PASSWORD']
    self.email = os.environ['TO_ADDRESS']

  def send(self, words):
    a,b,c,d,e = words

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(self.address, self.password)

    message = "From: %s\r\nSubject: %s\r\nTo: %s\r\n\r\n" % (self.address,"Hello From SendVibe!",self.email) + \
"Hey there!\n\nThanks for choosing to use SendVibe!!\n\nWe are busy at work analyzing the patterns in your emails, and we thought it would be fun to send you a word count!  Below are the top 5 words and how many of them are in your mailbox!\n\n{}\n{}\n{}\n{}\n{}\n\nBye for now!\n\nSendVibe <https://sendvibe.email>".format(a,b,c,d,e)
    
    ## Send that sucker out
    s.sendmail(self.address,self.email,message)

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
    for filename in os.listdir(self.data_folder):
      with open(self.data_folder +'/'+filename,'r') as infile:
        for line in infile:
          j = json.loads(line.strip())
          if 'payload' not in j:
            return
          count += 1
          if 'parts' in j['payload']:
            payload = j['payload']['parts']
          else:
            payload = [j['payload']]
          for part in payload:
            if part['mimeType'] == 'text/plain':
              msg = self.interpret(part['body']['data'])
              msg_clean = re.sub('[!@#$\.:,@\[\]]', '', msg).lower()
              msg_split = msg_clean.strip().split(" ")
              for word in msg_split:
                if word in self.stopwords:
                  continue
                if word not in self.words:
                  self.words[word] = 0
                self.words[word] += 1
                #print word, self.words[word]
    return self.words

c = Calc()
word_dict = c.analyze()
sorted_words = sorted(word_dict.items(), key=operator.itemgetter(1))
top_5_words = tuple(sorted_words[-5:])
words = ["{} - {} occurrences".format(k,v) for k,v in top_5_words]
words.reverse()

s = Send()
s.send(words)

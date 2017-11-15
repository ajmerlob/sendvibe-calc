import math
import os
import sys
import json

import base64
import email

print 'hello'

class Calc:
  def __init__(self):
    self.data_folder = "./data"

  def interpret(self,message):
    msg_str = base64.urlsafe_b64decode(message.encode('ASCII'))
    mime_msg = email.message_from_string(msg_str)
    return mime_msg


  ## ['payload']['headers'] is the metadata
  ## ['payload']['parts'] contains the data
  def analyze(self):
    count = 0
    for filename in os.listdir(self.data_folder):
      with open(self.data_folder +'/'+filename,'r') as infile:
        for line in infile:
          j = json.loads(line.strip())
          if 'payload' not in j:
            print count
            return
          count += 1
          if 'parts' in j['payload']:
            payload = j['payload']['parts']
          else:
            payload = [j['payload']]
          for part in payload:
            if part['mimeType'] == 'text/plain':
              print self.interpret(part['body']['data'])

c = Calc()
c.analyze()

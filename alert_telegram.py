import requests
import yaml
import imaplib
import mailparser
import hashlib
import os
from os import path

def save_to_file(set_name_file, input):
    with open(set_name_file, 'w', encoding='utf-8') as f:
        f.write(input)

class Mail_read:
    ''' Почтовый класс '''
    def mail_read_last_message(self):
        '''Чтение последнего письма'''
        # status, response = 
        # for uid in reversed(response[0].split()):
        #     status, response = self.imap.uid('fetch', uid, '(RFC822)')
        result, data = self.imap.uid('search', None, "ALL")
        latest_email_uid = data[0].split()[-1]
        result, data = self.imap.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        mail = mailparser.parse_from_bytes(raw_email)
        send_message = str(f"FROM {mail.from_[0][1]}")
        send_message = send_message +'\n' + str(mail.subject)
        for i in mail.text_plain:
            index = i.find('From')
            if index > 200:
                index=200
            send_message = send_message + '\n' + str(f"TEXT:{i[:index]}")
            send_message = send_message[:send_message.find('Disclaimer')]
        return send_message

    def mail_auth(self, config):
        '''Авторизация в почте'''
        self.imap = imaplib.IMAP4_SSL(config["mail"]["url"], 993)
        self.imap.login(config["mail"]["login"], config["mail"]["pass"])
        self.imap.select(config["mail"]["folder"])

def telegram(message_text):
    '''Отправка сообщений в телегу'''
    url = 'https://api.telegram.org/' + config["telegram"]["bot"]+ '/' + config["telegram"]["type_api"]
    data = { 'chat_id' : config["telegram"]["chat_id"] , 'text': message_text }
    response=requests.get(
    url ,
    params=data,
    headers={ 'Content-Type' : 'application/json' })
    if response.status_code == 200:
        print('SEND TELEGRAM : OK')
    else:
        print(response.status_code)
        print(response.text)

def hashsum(file):
    '''читает файл частями, возвращает хеш сумму'''
    if os.path.exists(file):
        with open(file, "rb") as fread:
            file_hash = hashlib.md5()
            while chunk := fread.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
#=============================
with open("config.yml", "r") as ymlfile:
    config = yaml.safe_load(ymlfile)

m=Mail_read()
m.mail_auth(config)
mail_all_test=m.mail_read_last_message()

if hashsum('message.txt') != hashlib.md5(mail_all_test.encode('utf-8')).hexdigest():
    # telegram(mail_all_test)
    save_to_file('message.txt',str(mail_all_test))


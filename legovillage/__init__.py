#!/usr/bin/python2.7

from time import sleep, time
from threading import Thread, Lock
from base64 import b64decode
from random import randint
import imaplib
import logging
import json

from Arduino import Arduino

config = json.load(open('legovillage.json', 'r'))
FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, filename=config.get('log_file'), 
    level=logging.INFO)


"""
Get total unread emails count.

@param config is a dict object containing the following imap server settings:
    imap_server - imap server address
    imap_port - imap server port
    imap_auth_type - type of authentication to use (cram_md5)
    imap_username - username to authenticate
    imap_passwd_file - file that contains base64 encoded password
    
    @returns the total number of unread emails
"""
def unread_email_count(config):
    imappasswd = b64decode(
        open(config.get('imap_passwd_file')).read())
        
    obj = imaplib.IMAP4_SSL(config.get('imap_server'), 
        config.get('imap_port'))

    if config.get('imap_auth_type') == 'cram_md5':
        obj.login_cram_md5(config.get('imap_username'), imappasswd)
    else:
        raise ValueError('Unknown imap auth type')

    obj.select('Inbox')
    res = obj.search(None,'UnSeen')[1][0]
    if res != "":
        unread_count = len(
            obj.search(None,'UnSeen')[1][0].split(' '))
    else:
        unread_count = 0

    return unread_count
        
"""
This function is the auxiliary worker thread, used to run synchronous
code (ex. checking email) and putting results inside a dict object.

"""
#TODO: use a Queue instead of dict object. 
def work(config, data):
    while 1:
        count = unread_email_count(config)
        logging.info("mail count: %d" % (count,))
        LegoVillage.worker_data_lock.acquire()
        running = data['running']
        data['unread_email_count'] = count
        LegoVillage.worker_data_lock.release()
        if not running:
            logging.info("Stopping work thread")
            break
        sleep(float(config.get('sleep_seconds')))


"""
This class represents the whole application.
It setups the arduino board, runs the auxiliary work thread, run the main loop
and control the LEDs.
"""
class LegoVillage:
    building1_floor0_lamp1 = 7
    building1_floor1_lamp1 = 4
    building2_floor1_lamp1 = 9
    building3_balcony_lamp1 = 8
    building3_hall_lamp1_rgb = (3, 5, 6)  # R, G, B
    worker_data_lock = Lock()

    def __init__(self, config):
        self.board = Arduino(str(config.get('arduino_baud')))
        for i in range(1, 14):
            self.board.pinMode(i, "OUTPUT")
        logging.info("Connected to Arduino")

        self.board.digitalWrite(self.building3_balcony_lamp1, "HIGH")
        self.board.digitalWrite(self.building2_floor1_lamp1, "HIGH")
        self.worker_data = dict()
        self.worker = Thread(target=work, 
            args=(dict(config), self.worker_data))

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            self._running = False
            LegoVillage.worker_data_lock.acquire()
            self.worker_data['running'] = False
            LegoVillage.worker_data_lock.release()
            self.worker.join()

    def _run(self):
        self._running = True
        self._last_mail_check = time()

        self.worker_data['running'] = True
        self.worker_data['unread_email_count'] = 0
        self.worker.start()
        unread_count = 0
        while self._running:
            LegoVillage.worker_data_lock.acquire()
            unread_count = self.worker_data['unread_email_count']
            LegoVillage.worker_data_lock.release()
            if unread_count > 0:
                self.board.digitalWrite(self.building1_floor0_lamp1, "HIGH")
                self.board.digitalWrite(self.building1_floor1_lamp1, "HIGH")
            else:
                self.board.digitalWrite(self.building1_floor0_lamp1, "LOW")
                self.board.digitalWrite(self.building1_floor1_lamp1, "LOW")

            self.board.analogWrite(self.building3_hall_lamp1_rgb[0], 
                int(randint(110, 255)))
            self.board.analogWrite(self.building3_hall_lamp1_rgb[1], 5)
            sleep(0.02)


def main():
    logging.info("Config loaded: %s" % (json.dumps(config),))
    village = LegoVillage(config)
    village.run()

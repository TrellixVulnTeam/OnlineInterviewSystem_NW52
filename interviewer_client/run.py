# coding=utf-8
# run.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: run app(interviewer client)
import time

from data.log import OISLog
from data.encryption import Encryption
from request import OISClientRequest
from user_manager import OISClientUserManager
from main import OIISInterviewerClient
from player import Player
from tts import Tts

import json


class BaseAbilities:

    def __init__(self):

        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))
        self.now_account = None
        self.account_token = None
        self.now_candidate = None

        self.log = OISLog()
        self.encryption = Encryption()
        self.main = None
        self.player = Player(self)
        self.tts = Tts(self)

        self.request = OISClientRequest(self)
        self.user_manager = OISClientUserManager(self)


if __name__ == "__main__":
    print("""
        ######################################
                OIIS-InterviewerClient
                   By Lanzhijiang
               lanzhijiang@foxmail.com
         2022-2022(c) all copyrights reserved
        ######################################
        """)
    ba = BaseAbilities()
    ic = OIISInterviewerClient(ba)
    ic.start()


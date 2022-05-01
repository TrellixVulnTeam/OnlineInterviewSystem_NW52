# coding=utf-8
# run.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: run app(candidate client)

from data.log import OISLog
from data.encryption import Encryption
from request import OISClientRequest
from user_manager import OISClientUserManager
from tts import Tts
from player import Player
import json
import time

from main import OIISClassClient


class BaseAbilities:

    def __init__(self):

        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))
        self.now_account = ""
        self.account_token = ""

        self.log = OISLog()
        self.encryption = Encryption()

        self.request = OISClientRequest(self)
        self.user_manager = OISClientUserManager(self)
        self.player = Player(self)
        self.tts = Tts(self)

        self.main = None


if __name__ == "__main__":
    print("""
        ######################################
                  OIIS-ClassClient
                   By Lanzhijiang
               lanzhijiang@foxmail.com
         2022-2022(c) all copyrights reserved
        ######################################
        """)
    ba = BaseAbilities()
    clc = OIISClassClient(ba)
    clc.start()


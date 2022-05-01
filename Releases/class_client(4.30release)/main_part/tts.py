# coding=utf-8
# author: Lan_zhijiang
# description: tts class
# date: 2022/4/24
import time

import requests
import threading
import urllib.request
import urllib.parse
import queue


class Tts:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.tts_setting = ba.setting["tts"]
        self.player = ba.player

        self.token = ""
        self.app_id = self.tts_setting["appId"]
        self.api_key = self.tts_setting["apiKey"]
        self.secret_key = self.tts_setting["secretKey"]

        self.tts_queue = queue.Queue()
        self.is_working = False

        self.get_token()

    def get_token(self):

        """
        获取token
        :return:
        """
        param = {'grant_type': 'client_credentials',
                 'client_id': self.api_key,
                 'client_secret': self.secret_key}
        params = urllib.parse.urlencode(param)
        # ?grant_type=client_credentials&client_id=%s&client_secret=%s' % (self.app_id, self.secret_key)
        r = requests.get('https://aip.baidubce.com/oauth/2.0/token', params=params, timeout=10)
        try:
            if r.status_code == 200:
                self.log.add_log("Tts: get token success", 1)
                token = r.json()['access_token']
                self.token = token
                return token
            else:
                self.log.add_log("Tts: get token failed, code-%s" % r.status_code, 3)
        except requests.exceptions.HTTPError:
            self.log.add_log("Tts: failed to get token, http error, code-%s " % r.status_code, 3)
            return ""

    def start(self, text, is_play=True):

        """
        开始生成语音
        :param text: 要转换的文本
        :param is_play: 是否立即播放
        :return:
        """
        self.log.add_log("Tts: received tts call, add to queue", 1)
        self.tts_queue.put([text, is_play])

        tts_thread = threading.Thread(target=self.real_tts, args=())
        tts_thread.start()

    def real_tts(self):

        """
        真正的tts，线程启动
        :return:
        """
        while self.is_working:
            time.sleep(0.5)

        self.is_working = True
        call_param = self.tts_queue.get()
        text_, is_play_ = call_param[0], call_param[1]
        self.log.add_log("Tts: start tts, text-%s" % text_, 1)
        text_ = urllib.parse.quote_plus(text_)
        data = {
            'tex': text_,
            'lan': 'zh',
            'tok': self.token,
            'ctp': 1,
            'cuid': 'hadream_assistant',
            'per': self.tts_setting["per"],
            'aue': 6,
            "spd": 5
        }

        data = urllib.parse.urlencode(data)
        req = urllib.request.Request('http://tsn.baidu.com/text2audio',
                                     data.encode('utf-8'))

        f = urllib.request.urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        if "audio" in headers["content-type"]:
            self.log.add_log("Tts: tts request succeed", 1)
            with open("./data/audio/say.wav", "wb+") as f:
                f.write(result_str)
            if is_play_:
                self.player.say()
                self.is_working = False
            return True
        else:
            self.log.add_log("Tts: Tts meet an error! Response: %s" % str(result_str), 3)
            self.is_working = False
            return False

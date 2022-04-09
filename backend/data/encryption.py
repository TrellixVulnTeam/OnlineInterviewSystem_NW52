# coding=utf-8
# author: Lan_zhijiang
# desciption: 加密
# date: 2020/11/1

import hashlib
import string
import random


class Encryption:

    def __init__(self):

        self.md5_ = hashlib.md5()
        self.sha1_ = hashlib.sha1()

    def md5(self, string_):

        """
        进行md5加密 32位！
        :param string_:
        :return:
        """
        self.md5_.update(string_.encode("utf-8"))
        return self.md5_.hexdigest()

    def sha1(self, string_):

        """
        进行sha1加密
        :param string_:
        :return:
        """
        self.sha1_.update(string_.encode("utf-8"))
        return self.sha1_.hexdigest()

    def generate_random_key(self):

        """
        生成随机钥匙
        :return:
        """
        maka = string.digits + string.ascii_letters
        maka_list = list(maka)
        x = [random.choice(maka_list) for i in range(6)]
        return ''.join(x)

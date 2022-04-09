# coding=utf-8
# request.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: to request the backend

import json
import requests


class OISClientRequest:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.request_url = self.setting["requestUrl"]

        self.encryption = self.ba.encryption
        self.request_template = json.load(open("./data/json/request_template.json", "r", encoding="utf-8"))

    def basic_request(self, path, body, method):

        """
        请求基本函数
        :param path: 请求路径
        :param body: 请求体
        :param method: 模式
        :return:
        """
        self.log.add_log("Request: carry on basic_request, method-%s" % method, 1)

        url = self.request_url + path
        body["header"]["timeStamp"] = self.log.get_time_stamp()
        if method == "GET":
            r = requests.get(url=url, data=body)
        elif method == "POST":
            r = requests.post(url=url, data=body)
        elif method == "PUT":
            r = requests.put(url=url, data=body)
        elif method == "PATCH":
            r = requests.patch(url=url, data=body)
        elif method == "DELETE":
            r = requests.delete(url=url, data=body)
        else:
            self.log.add_log("Request: invalid method-%s" % method)
            return False, None

        if r.status_code == 200:
            self.log.add_log("Request: request success", 1)
            return True, r
        else:
            self.log.add_log("Request: request failed", 3)
            return False, r

    def user_login(self, account, password):

        """
        请求-用户登录
        :param account: 账号
        :param password: 密码(raw)
        :return:
        """
        self.log.add_log("Request: do user_login request, account-%s" % account, 1)

        # 长度效验(candidate login)
        if len(account) != 5:
            self.log.add_log("Request: user_login fail, account length should be 5 but not", 3)
            return False, "wrong account length"

        password = self.encryption.md5(password)
        body = self.request_template
        body["header"]["loginRequest"] = True

        command = {
            "commandName": "user_login",
            "param": {
                "account": account,
                "password": password,
                "userType": "candidate"
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api/", body, "POST")
        if res:
            res = r.json()
            if res["header"]["status"] == 0:
                self.log.add_log("Request: login success", 1)
                token = res["response"][0]["token"]
                return True, token
            else:
                self.log.add_log("Request: login failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                return False, res["header"]["errorMsg"]
        else:
            self.log.add_log("Request: login fail. request meet error, code-%s" % r.status_code, 3)

    def user_logout(self, account):

        """
        请求-用户登出
        :param account: 账户名
        :return:
        """
        self.log.add_log("Request: do user_logout request, account-%s" % account, 1)

        # 长度效验(candidate login)
        if len(account) != 5:
            self.log.add_log("Request: user_logout fail, account length should be 5 but not", 3)
            return False, "wrong account length"

        body = self.request_template
        command = {
            "commandName": "user_logout",
            "param": {
                "account": account,
                "userType": "candidate"
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api/", body, "POST")
        if res:
            res = r.json()
            if res["header"]["status"] == 0:
                self.log.add_log("Request: logout success", 1)
                return True, ""
            else:
                self.log.add_log("Request: logout failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                return False, res["header"]["errorMsg"]
        else:
            self.log.add_log("Request: logout fail. request meet error, code-%s" % r.status_code, 3)

    def user_get_info(self, account, keys):

        """
        请求-获取用户信息
        :param account: 用户名
        :param keys: 要获取的信息的键 list
        :return:
        """
        self.log.add_log("Request: do user_get_info request, account-%s" % account, 1)

        # 长度效验(candidate login)
        if len(account) != 5:
            self.log.add_log("Request: user_get_info fail, account length should be 5 but not", 3)
            return False, "wrong account length"

        body = self.request_template
        command = {
            "commandName": "user_get_info",
            "param": {
                "account": account,
                "keys": keys
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api/", body, "POST")
        if res:
            res = r.json()
            if res["header"]["status"] == 0:
                self.log.add_log("Request: user_get_info success", 1)
                return True, res["response"][0]["userInfo"]
            else:
                self.log.add_log("Request: user_get_info failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                return False, res["header"]["errorMsg"]
        else:
            self.log.add_log("Request: user_get_info fail. request meet error, code-%s" % r.status_code, 3)

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
        self.now_account = ba.now_account
        self.account_token = ba.account_token

        self.request_url = self.setting["requestUrl"]

        self.encryption = self.ba.encryption

    def get_body(self):

        """
        get request body template
        :return:
        """
        res = json.load(open("./data/json/request_template.json", "r", encoding="utf-8"))
        res["header"]["userType"] = self.setting["userType"]
        res["header"]["account"] = self.now_account
        res["header"]["token"] = self.account_token
        return res

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

        body = json.dumps(body)
        print(body)
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
        body = self.get_body()
        body["header"]["loginRequest"] = True

        command = {
            "commandName": "user_login",
            "param": {
                "account": account,
                "password": password,
                "userType": self.setting["userType"]
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api", body, "POST")
        if res:
            res = r.json()
            if res["header"]["status"] == 0:
                try:
                    token = res["response"][0]["result"]["token"]
                except KeyError:
                    self.log.add_log("Request: login failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                    return False, res["header"]["errorMsg"]
                else:
                    self.log.add_log("Request: login success", 1)
                    return True, token
            else:
                self.log.add_log("Request: login failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                return False, res["header"]["errorMsg"]
        else:
            self.log.add_log("Request: login fail. request meet error, code-%s" % r.status_code, 3)
            return False, res

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

        body = self.get_body()
        command = {
            "commandName": "user_logout",
            "param": {
                "account": account,
                "userType": self.setting["userType"]
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api", body, "POST")
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

    def user_info_get_multi(self, account, keys):

        """
        请求-获取用户信息，一个用户的多个信息
        :param account: 用户名
        :param keys: 要获取的信息的键 list
        :return:
        """
        self.log.add_log("Request: do user_info_get_multi request, account-%s" % account, 1)

        # 长度效验(candidate login)
        if len(account) != 5:
            self.log.add_log("Request: user_info_get_multi fail, account length should be 5 but not", 3)
            return False, "wrong account length"

        body = self.get_body()
        command = {
            "commandName": "user_info_get_one_multi",
            "param": {
                "account": account,
                "userType": self.setting["userType"],
                "keys": keys
            }
        }
        body["command"].append(command)
        res, r = self.basic_request("/api", body, "POST")
        if res:
            res = r.json()
            if res["header"]["status"] == 0:
                self.log.add_log("Request: user_info_get_multi success", 1)
                return True, res["response"][0]["result"]
            else:
                self.log.add_log("Request: user_info_get_multi failed, err_msg-%s" % res["header"]["errorMsg"], 3)
                return False, res["header"]["errorMsg"]
        else:
            self.log.add_log("Request: user_info_get_multi fail. request meet error, code-%s" % r.status_code, 3)

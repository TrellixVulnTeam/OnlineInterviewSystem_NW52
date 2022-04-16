# coding=utf-8
# user_manager.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: handle everything about user operation: login logout get_info


class OISClientUserManager:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.request = ba.request

    def login(self, account, password):

        """
        进行登录
        :param account: 账号名
        :param password: 密码
        :return:
        """
        self.log.add_log("UserManager: try login user-%s" % account, 1)

        sta, res = self.request.user_login(account, password)
        if sta:
            self.ba.now_account = account
            self.ba.account_token = res
            self.log.add_log("UserManager: login success, now account: %s" % account, 1)
            return True
        else:
            self.log.add_log("UserManager: login failed", 3)
            return False

    def logout(self):

        """
        登出当前用户
        :return:
        """
        self.log.add_log("UserManager: try logout user-%s" % self.ba.now_account, 1)
        if self.ba.now_account is None:
            self.log.add_log("UserManager: can't logout, no user logged in", 3)
            return False

        sta, res = self.request.user_logout(self.ba.now_account)
        if sta:
            self.ba.now_account = None
            self.ba.account_token = None
            self.log.add_log("UserManager: logout success", 1)
            return True
        else:
            self.log.add_log("UserManager: logout failed", 3)
            return False

    def get_user_interview_info(self):

        """
        获取当前用户的面试信息
        :return:
        """
        self.log.add_log("UserManager: try get user-%s's interview info" % self.ba.now_account, 1)
        if self.ba.now_account is None:
            self.log.add_log("UserManager: can't get info, no user logged in", 3)

        sta, res = self.request.user_get_info(self.ba.now_account, ["interviewInfo"])
        if sta:
            self.ba.now_account = None
            self.ba.account_token = None
            self.log.add_log("UserManager: get user interview info success", 1)
            return True
        else:
            self.log.add_log("UserManager: get user interview info failed", 3)
            return False

    def get_enterprise_interview_info(self):

        """
        获取企业面试信息
        :return:
        """



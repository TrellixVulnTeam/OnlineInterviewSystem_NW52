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

        # verify is the account in interview_list
        if account != "00000":
            if account not in self.setting["interviewCandidateQueue"]:
                self.log.add_log("UserManager: account-%s does not pair to this client, login not allowed" % account, 3)
                return False

        # if int(account[-1]) != self.ba.interview_phase:
        #     self.log.add_log("UserManager: account-%s does not pair to the phase, login not allowed" % account, 3)
        #     return False

        res, err = self.request.user_login(account, password)
        if res is not False:
            self.ba.now_account = account
            self.ba.account_token = res
            self.log.add_log("UserManager: login success, now account: %s" % account, 1)
            return True
        else:
            self.log.add_log("UserManager: login failed, err-%s" % err, 3)
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

        res, err = self.request.user_logout(self.ba.now_account)
        if res:
            self.ba.now_account = None
            self.ba.account_token = None
            self.log.add_log("UserManager: logout success", 1)
            return True
        else:
            self.log.add_log("UserManager: logout failed, err-%s" % err, 3)
            return False

    def get_user_interview_info(self):

        """
        获取当前用户的面试信息
        :return:
        """
        self.log.add_log("UserManager: try get user-%s's interview info" % self.ba.now_account, 1)
        if self.ba.now_account is None:
            self.log.add_log("UserManager: can't get info, no user logged in", 3)

        res, err = self.request.user_info_get_multi(self.ba.now_account, ["class", "nickname"])
        if res is not False:
            self.log.add_log("UserManager: get user interview info success", 1)
            res = res["userInfo"]
            res["code"] = self.ba.now_account
            return res
        else:
            self.log.add_log("UserManager: get user interview info failed, err-%s" % err, 3)
            return False


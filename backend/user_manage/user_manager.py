# coding=utf-8
# author: Lan_zhijiang
# description: 用户管理器
# date: 2020/10/2

import json
from user_manage.user_info_operator import UserInfoManager


class UserManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.ws_conn_list = base_abilities.ws_conn_list

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.encryption = self.base_abilities.encryption
        self.user_info_manager = UserInfoManager(self.base_abilities)

    def sign_up(self, account, password, user_type):

        """
        注册用户
        :param account: 账户名
        :param password: 密码(md5)
        :param user_type: 用户类型 candidate enterprise root class
        :return bool
        """
        if "/" in account or "." in account or "-" in account:
            self.log.add_log("UserManager: '/', '.' and '-' is banned in account name", 3)
            return False, "account not in law"

        if self.mongodb_manipulator.is_collection_exist(user_type, account) is True:
            self.log.add_log("UserManager: Sign up fail, this user had already exists. sign up account: " + account, 3)
            return False, "user had already exists"

        if self.mongodb_manipulator.add_collection(user_type, account) is False:
            self.log.add_log("UserManager: Sign up failed, something wrong while add account. sign up account: " + account, 3)
            return False, "add user went wrong"
        else:
            self.log.add_log("UserManager: Account add to the collection: user successfully", 1)

        # fill user info
        password = self.encryption.md5(password)

        user_info = json.load(open("./data/json/user_info_template.json", "r", encoding="utf-8"))
        user_info[0]["account"] = account
        user_info[1]["password"] = password
        user_info[2]["userType"] = user_type  # 未做校验

        # update user info into database
        if self.mongodb_manipulator.add_many_documents(user_type, account, user_info) is False:
            self.log.add_log("UserManager: Sign up failed, something wrong with database, user-%s" % account, 3)
            return False, "database error"
        else:
            # init user info(nickname interview_info)
            err = ""
            self.log.add_log("UserManager: Sign up user-%s done" % account, 1)
            return True, err

    def login(self, account, password, user_type, com_code=None):

        """
        登录
        :param account: 账户
        :param password: 密码
        :param user_type: 用户类型 candidate interviewer class root
        :param com_code: 面试终端编号 candidate/interviewer才需要
        :return: bool(fail) str(success)
        """
        self.log.add_log("UserManager: Try login " + account, 1)

        user_info, res = self.user_info_manager.get_one_user_multi_info(account, user_type, ["password", "user_type"])
        if user_info is False:
            self.log.add_log("UserManager: login: Can't find your account or something wrong in the mongodb "
                             "or user-%s does not exist." % account, 3)
            return False, "database error or user-%s not exist" % account
        else:
            print(password)
            password = self.encryption.md5(password)
            print(password, user_info["password"])
            if password == user_info["password"]:
                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 6}, {"isOnline": True})

                token = self.encryption.md5(self.log.get_time_stamp() + account)
                last_login_time_stamp = self.log.get_time_stamp()

                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 5}, {"lastLoginTimeStamp": last_login_time_stamp})
                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 4}, {"token": token})

                self.log.add_log("UserManager: login success", 1)

                if user_type == "candidate":
                    a = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
                    com_status = a["status"]  # offline candidate_online interviewer_online ready in_interview
                    interviewer_code = a["bindInterviewer"]
                    if com_status == "offline":
                        self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "candidate_online"})
                    elif com_status == "interviewer_online" or com_status == "ready" or com_status == "in_interview":
                        self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "ready"})
                        # send candidate info
                        try:
                            self.ws_conn_list["interviewer"][interviewer_code].send_command("candidate_online", {"candidateCode": account})
                        except KeyError:
                            self.log.add_log("UserManager: interviewer-%s does not online" % interviewer_code, 1)
                elif user_type == "interviewer":
                    com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
                    com_status = com_info["status"]  # offline candidate_online interviewer_online ready in_interview
                    if com_status == "candidate_online":
                        self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "ready"})
                    elif com_status == "offline":
                        self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "interviewer_online"})

                return token, "success"
            else:
                self.log.add_log("UserManager: Your password or username is wrong", 1)
                return False, "wrong password or username"

    def logout(self, account, user_type, com_code=None):

        """
        登出
        :param account: 要登出的账户名
        :param user_type: 用户类型 candidate interviewer class root
        :param com_code: 面试终端编号
        :return:
        """
        self.log.add_log("UserManager: Try logout " + account, 1)

        is_online = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document(user_type, account, {"isOnline": 1}, 2),
            ["isOnline"]
        )[0]["isOnline"]
        if is_online:
            self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 4}, {"token": None})
            self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 6}, {"isOnline": False})

            if user_type == "candidate":
                com_status = list(
                    self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]["status"]  # offline candidate_online interviewer_online ready in_interview
                if com_status == "ready" or com_status == "in_interview":
                    self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "interviewer_online"})
                elif com_status == "candidate_online":
                    self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "offline"})
            elif user_type == "interviewer":
                com_code = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("interviewer", account, {"_id": 8}, 1),
                    ["mappingComCode"]
                )[0]["mappingComCode"]
                com_status = list(
                    self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]["status"]  # offline candidate_online interviewer_online ready in_interview
                if com_status == "ready" or com_status == "in_interview":
                    self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "candidate_online"})
                elif com_status == "interviewer_online":
                    self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"status": "offline"})

            self.log.add_log("UserManager: logout success", 1)
            return True, "success"
        else:
            self.log.add_log("UserManager: user: " + account + " have't login yet, can't logout", 1)
            return False, "user haven't login yet, can't logout"

    def reset_password(self, account, new_password, user_type):

        """
        修改密码
        :param account: 账户名
        :param new_password: 密码名称
        :param user_type: 用户类型
        :return: bool, str
        """
        self.log.add_log("UserManager: Try reset user-%s's password" % account, 1)

        is_online = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document(user_type, account, {"isOnline": 1}, 2),
            ["isOnline"]
        )[0]["isOnline"]
        if is_online:
            password = self.encryption.md5(new_password)
            self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 1}, {"password": password})

            self.logout(account, user_type)
            return True, "success"
        else:
            self.log.add_log("UserManager: user: " + account + " have't login yet, can't reset the password", 1)
            return False, "user haven't login yet, can't reset the password"


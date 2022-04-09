# coding=utf-8
# author: Lan_zhijiang
# description: 用户管理器
# date: 2020/10/2

import json
from user.user_info_operator import UserInfoManager


class UserManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.encryption = self.base_abilities.encryption
        self.user_info_manager = UserInfoManager(self.base_abilities)

    def sign_up(self, account, password, user_type="default"):

        """
        注册用户
        :param account: 账户名
        :param password: 密码(md5)
        :param user_type: 用户类型 candidate enterprise root
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
        user_info[2]["userType"] = user_type # 未做校验

        # update user info into database
        if self.mongodb_manipulator.add_many_documents(user_type, account, user_info) is False:
            self.log.add_log("UserManager: Sign up failed, something wrong with database, user-%s" % account, 3)
            return False, "database error"
        else:
            # init user info(nickname interview_info)
            self.log.add_log("UserManager: Sign up user-%s done" % account, 1)
            return True, err

    def login(self, account, password, user_type):

        """
        登录
        :param account: 账户
        :param password: 密码
        :param user_type: 用户类型 candidate enterprise root
        :return: bool(fail) str(success)
        """
        self.log.add_log("UserManager: Try login " + account, 1)

        user_info, res = self.user_info_manager.get_one_user_multi_info(account, ["password", "user_type"])
        if user_info is False:
            self.log.add_log("UserManager: login: Can't find your account or something wrong in the mongodb "
                             "or user-%s does not exist." % account, 3)
            return False, "database error or user-%s not exist" % account
        else:
            password = self.encryption.md5(password)
            if password == user_info["password"]:
                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 6}, {"isOnline": True})

                token = self.encryption.md5(self.log.get_time_stamp() + account)
                last_login_time_stamp = self.log.get_time_stamp()

                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 5}, {"lastLoginTimeStamp": last_login_time_stamp})
                self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": 4}, {"token": token})

                self.log.add_log("UserManager: login success", 1)
                return token, "success"
            else:
                self.log.add_log("UserManager: Your password or username is wrong", 1)
                return False, "wrong password or username"

    def logout(self, account, user_type):

        """
        登出
        :param account: 要登出的账户名
        :param user_type: 用户类型 candidate enterprise root
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


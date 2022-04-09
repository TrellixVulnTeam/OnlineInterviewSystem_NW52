# coding=utf-8
# author: Lan_zhijiang
# description 本地api
# date: 2022/4/9

from user_manager.user_manager import UserManager
from user_manager.user_info_operator import UserInfoManager


class LocalCaller:

    def __init__(self, base_abilities, caller):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting
        self.caller = caller

        if self.caller == "root":
            self.not_root = False
        else:
            self.not_root = True

        self.user_manager = UserManager(self.base_abilities)
        self.user_info_manager = UserInfoManager(self.base_abilities)

    def user_login(self, param):

        """
        用户登录
        :return:
        """
        self.log.add_log("LocalCaller: start user_login", 1)

        result = {}

        try:
            account = param["account"]
            password = param["password"]
            user_type = param["userType"]
        except KeyError:
            self.log.add_log("LocalCaller: user_login: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.login(account, password, user_type)
            if res is False:
                return False, err
            else:
                result["token"] = res
                return result, err

    def user_logout(self, param):

        """
        用户登出
        :return:
        """
        self.log.add_log("LocalCaller: start user_logout", 1)

        try:
            account = param["account"]
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.logout(account)
            return res, err

    def user_sign_up(self, param):

        """
        用户注册
        :return:
        """
        self.log.add_log("LocalCaller: start user_sign_up", 1)

        result = {}
        try:
            account = param["account"]
            password = param["password"]
            user_type = param["userType"]
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.sign_up(account, password, user_type)
            if res is False:
                return False, err
            else:
                return result, err

    def user_info_update(self, param):

        """
        更新用户信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_update", 1)
        res, err = False, ""

        result = {}
        try:
            account = param["account"]
            info = param["info"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_update: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to change other user's info"
                elif self.caller == account and "permissionsList" in info:
                    err = "you are not allowed to change your own permissionsList"
                if err != "":
                    return res, err

            res, err = self.user_info_manager.update_user_info(account, info)

            if res is False:
                return res, err
            else:
                return result, err

    def user_info_get_all(self, param):

        """
        获取用户所有信息(WARNING: ONLY ROOT CAN OWN)
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_all", 1)

        result = {}
        try:
            accounts = param["accounts"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_all: Your param is incomplete", 3)
            return False, "param incomplete, attention, it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_users_all_info(accounts)
            if res is False:
                return res, err
            else:
                result["usersInfo"] = res
                return result, err

    def user_info_get_one_multi(self, param):

        """
        获取一个用户的多个信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_one_multi", 1)

        result = {}
        res, err = False, ""

        try:
            account = param["account"]
            keys = param["keys"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_one_multi: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to get other user's info"
                    return res, err

            res, err = self.user_info_manager.get_one_user_multi_info(account, keys)

            result["userInfo"] = res
            return result, err

    def user_info_get_multi_multi(self, param):

        """ root only
        获取多个用户的多个信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_multi_multi", 1)

        result = {}
        try:
            accounts = param["accounts"]
            keys = param["keys"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_multi_multi: Your param is incomplete", 3)
            return False, "param incomplete, caution! it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_multi_users_multi_info(accounts, keys)
            result["usersInfo"] = res
            return result, err

    # def stuff_add(self, param):
    #
    #     """
    #     添加stuff到inbox
    #     :param param:
    #     :return:
    #     """
    #     self.log.add_log("LocalCaller: stuff_add", 1)
    #
    #     try:
    #         account = param["account"]
    #         content = param["content"]
    #         create_date = param["createDate"]
    #         lots = param["lastOperateTimeStamp"]
    #     except KeyError:
    #         self.log.add_log("LocalCaller: user_group_get_permissions: Your param is incomplete", 3)
    #         return False, "param incomplete"
    #     else:
    #         if self.not_root:
    #             if self.caller != account:
    #                 err = "you are not allowed to add stuff into other user's inbox"
    #                 return False, err
    #
    #         optional_param = ["description", "tags", "links", "time", "place", "level", "status"]
    #         desc, tags, links, time, place, level, status = None, [], [], None, None, 0, "wait_classify"
    #         for key in optional_param:
    #             try:
    #                 if key == "description":
    #                     desc = param["description"]
    #                 elif key == "tags":
    #                     tags = param["tags"]
    #                 elif key == "links":
    #                     links = param["links"]
    #                 elif key == "time":
    #                     time = param["time"]
    #                 elif key == "place":
    #                     place = param["place"]
    #                 elif key == "level":
    #                     level = param["level"]
    #                 elif key == "status":
    #                     status = param["status"]
    #             except KeyError:
    #                 pass
    #
    #         res, err = self.inbox_manager.add_stuff(account, content, create_date, lots, desc=desc, tags=tags, links=links, time=time, place=place, level=level, status=status)
    #         return res, err


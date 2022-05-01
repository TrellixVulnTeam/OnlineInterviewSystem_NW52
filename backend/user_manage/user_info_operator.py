# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户信息管理器
# date: 2020/10/17

import json
import time


class UserInfoManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator

        self.candidate_info_id_event_mapping = json.load(open("./data/json/candidate_info_id_event_mapping.json", "r", encoding="utf-8"))
        self.interviewer_info_id_event_mapping = json.load(open("./data/json/interviewer_info_id_event_mapping.json", "r", encoding="utf-8"))
        self.candidate_info_keys = list(self.candidate_info_id_event_mapping.keys())
        self.interviewer_info_keys = list(self.interviewer_info_id_event_mapping.keys())

    def update_user_info(self, account, user_type, info, special_allow=False):

        """
        更新用户信息
        :param account: 账户名
        :param info: 要更新的信息
        :param user_type: 用户类型
        :param special_allow: 特别允许：用于sign_up
        :type info: dict
        :return bool, str
        """
        not_found_keys = []
        res, err = True, ""
        if type(info) != dict:
            self.log.add_log("UserInfoManager: Failed to update user info: info must be a dict", 3)
            return False, "the type of info is wrong"

        if user_type == "candidate":
            event_id_mapping = self.candidate_info_id_event_mapping
        elif user_type == "interviewer":
            event_id_mapping = self.interviewer_info_id_event_mapping
        else:
            event_id_mapping = self.candidate_info_id_event_mapping

        key_list = info.keys()
        for key in key_list:
            try:
                if key == "permissionsList" and account != "root":
                    if special_allow is False:
                        self.log.add_log("UserInfoManager: It's not allow normal user to change permissionsList", 1)
                        raise KeyError

                if self.mongodb_manipulator.update_many_documents(user_type, account, {"_id": event_id_mapping[key]}, {key: info[key]}) is False:
                    self.log.add_log("UserInfoManager: meet database error while updating " + key + ", skip and wait", 3)
                    res, err = False, "database error"
                    time.sleep(0.1)
                    continue
            except KeyError:
                self.log.add_log("UserInfoManager: cannot find " + key + ", in your info list, or permission denied", 3)
                not_found_keys.append(key)
                res, err = False, "key-%s" % not_found_keys + " does not exists or '_id' is not exists"
                continue

        return res, err

    def get_users_all_info(self, accounts, user_types):

        """
        获取用户所有信息（可多个用户）
        :type accounts: list
        :param accounts: 账户名
        :param user_types: 用户类型
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserInfoManager: param-account must be a list!", 3)
            return False, "the type of param is wrong"

        users_info = {}
        not_found_users = []
        res = "success"

        for i in range(0, len(accounts)):
            account = accounts[i]
            self.log.add_log("UserInfoManager: Getting user-" + str(account) + "'s info", 1)
            raw_user_info = self.mongodb_manipulator.get_document(user_types[i], account, mode=0)
            if raw_user_info is False:
                not_found_users.append(account)
                self.log.add_log("UserInfoManager: Can't find user-%s" % account, 1)

            user_info = {}
            for info in raw_user_info:
                key = list(info.keys())[-1]
                user_info[key] = info[key]

            users_info[account] = user_info

        if not_found_users:
            res = "user-" + str(not_found_users) + " is not exist"
        return users_info, res

    def get_one_user_multi_info(self, account, user_type, keys):

        """
        获取单个用户的信息（支持多个信息，但只支持单个用户）
        :type keys: list
        :param user_type: 用户类型
        :param keys: 要查询的keys
        :param account: 账户名
        :return:
        """
        result = {}
        not_found_keys = []
        res = "success"

        if user_type == "candidate":
            user_info_keys = self.candidate_info_keys
        elif user_type == "interviewer":
            user_info_keys = self.interviewer_info_keys
        else:
            user_info_keys = self.candidate_info_keys


        for key in keys:
            self.log.add_log("UserInfoManager: try to get user- " + account + "'s " + key, 1)

            if key in user_info_keys:
                result_ = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document(user_type, account, {key: 1}, 2),
                    [key]
                )
                print(result_)
                result[key] = result_[0][key]
            else:
                not_found_keys.append(key)
                continue

        if not_found_keys:
            res = "key-" + str(not_found_keys) + " is not exist"
        return result, res

    def get_multi_users_multi_info(self, accounts, user_types, keys):

        """
        获取多个用户多个信息
        :type keys: dict
        :type accounts: list
        :param accounts: 账户名列表 list
        :param user_types: 用户类型列表 list
        :param keys: 要查询的keys，dict{account: [key, key, key]}
        :return:
        """
        result = {}
        info_not_found_users = []
        err = "success"

        if type(keys) != dict:
            self.log.add_log("UserInfoManager: In get_multi_multi_info, param-keys must be a dict", 3)
            return False, "param-keys type error"

        for i in range(0, len(accounts)):
            account = accounts[i]
            self.log.add_log("UserInfoManager: try to get user-%s's multi info" % account, 1)

            if self.mongodb_manipulator.is_collection_exist(user_types[i], account) is False:
                self.log.add_log("UserInfoManager: user-%s is not exist" % account, 1)
                info_not_found_users.append(account)
                continue

            result_, err_ = self.get_one_user_multi_info(account, user_types[i], keys[account])

            if err_ != "success":
                self.log.add_log("UserInfoManager: " + err_, 1)
                info_not_found_users.append(account)
                continue

            result[account] = result_

        if info_not_found_users:
            err = "user-" + str(info_not_found_users) + "'s info can't be found or user not exist"
        return result, err

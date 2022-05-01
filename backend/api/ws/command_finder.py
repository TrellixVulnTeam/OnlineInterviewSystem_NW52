# coding=utf-8
# author: Lan_zhijiang
# description: http command finder
# date: 2022/4/9

from api.local.local_caller import LocalCaller


class CommandFinder:

    def __init__(self, base_abilities, caller, user_type):

        self.local_caller = LocalCaller(base_abilities, caller, user_type)

        self.all_command_list = {
            "user_login": self.local_caller.user_login,
            "user_logout": self.local_caller.user_logout,
            "user_sign_up": self.local_caller.user_sign_up,
            "user_info_update": self.local_caller.user_info_update,
            "user_info_get_all": self.local_caller.user_info_get_all,
            "user_info_get_one_multi": self.local_caller.user_info_get_one_multi,
            "user_info_get_multi_multi": self.local_caller.user_info_get_multi_multi,

        }

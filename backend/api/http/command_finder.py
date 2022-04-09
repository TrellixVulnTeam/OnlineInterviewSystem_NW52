# coding=utf-8
# author: Lan_zhijiang
# description: http command finder
# date: 2022/4/9

from backend.api.local.local_caller import LocalCaller


class CommandFinder:

    def __init__(self, base_abilities, caller):

        self.local_caller = LocalCaller(base_abilities, caller)

        self.all_command_list = {
        }

# coding=utf-8
# author: Lan_zhijiang
# description: system run
# date: 2022/4/9

from init import BackendInit

backend_init = BackendInit()

if __name__ == "__main__":
    print("""
    ######################################
        OnlineInterviewSystem-Backend
               By Lanzhijiang
           lanzhijiang@foxmail.com
     2022-2022(c) all copyrights reserved
    ######################################
    """)
    backend_init.run_backend()

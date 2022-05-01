# coding=utf-8
# ws_client.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/27
# description: parcel resume

import json
import os
import shutil


class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
name_logs_mapping = json.load(open("./data/json/candidate_name_code_mapping.json", "r", encoding="utf-8"))
parent_dir = "F:/Files/班级收集简历"
sub_dirs = os.listdir(parent_dir)
all_dirs = {}
for sub_dir in sub_dirs:
    sub_dir_files = os.listdir(parent_dir + "/%s" % sub_dir)
    all_dirs[sub_dir] = []
    for file in sub_dir_files:
        all_dirs[sub_dir].append(file)
reassign_interview_candidate_list = json.load(open("./data/json/interview_apply_info_all.json", "r", encoding="utf-8"))


for enterprise_id in list(reassign_interview_candidate_list.keys()):
    print("NOW PROCESS ENTERPRISE-%s" % enterprise_id)
    enterprise_dir = "F:\Files\简历打包\%s" % enterprise_id
    try:
        os.mkdir(enterprise_dir)
    except FileExistsError:
        pass

    candidate_list = reassign_interview_candidate_list[enterprise_id]
    for candidate in candidate_list:
        print("  NOW LOOKING FOR %s's RESUME" % candidate)
        for sub_dir in list(all_dirs.keys()):
            if len(sub_dir) == 1:
                sub_dir_str = "0%s" % sub_dir
            else:
                sub_dir_str = str(sub_dir)
            if int(sub_dir) in class_1:
                p = "1"
            else:
                p = "2"
            for file in all_dirs[sub_dir]:
                print("  search file-%s " % file)
                file_name, file_type = os.path.splitext(file)
                if len(file_name) == 2 and file_name.isdigit():
                    file_name = sub_dir_str + file_name + p
                    print("    RENAME TO %s" % file_name)
                elif (len(file_name) == 3 or len(file_name) == 2 or len(file_name) == 4) and not file_name.isdigit():
                    try:
                        file_name = name_logs_mapping[file_name]
                    except KeyError:
                        pass

                if candidate in file_name:
                    print("    FOUND, ADD")
                    try:
                        shutil.copyfile("%s/%s/%s" % (parent_dir, sub_dir, file), enterprise_dir + "/%s" % file_name + file_type)
                    except FileExistsError:
                        pass
                    break



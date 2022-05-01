# 转登分号电子表到json文件

import xlrd
import json
import os

file_name = "./data/腾讯会议链接.xls"
sheet = xlrd.open_workbook(file_name).sheet_by_index(0)
class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
class_all = list(range(1, 32))
row_a = 1
# all_logs = {}
#
# for class_name in class_all:
#
#     print("now process class-%s" % class_name)
#     if class_name in class_1:
#         p = "1"
#     else:
#         p = "2"
#
#     class_name = str(class_name)
#     class_logs = {}
#
#     if len(class_name) == 1:
#         class_code = "0" + class_name
#     else:
#         class_code = class_name
#
#     for row_c in range(row_a, row_a+60):
#         box = {}
#         try:
#             class_now = str(int(sheet.cell_value(row_c, 0)))
#         except IndexError:
#             print(row_c)
#         else:
#             if class_now != class_name:
#                 print("  class now is different from class_name")
#                 continue
#
#             try:
#                 log = str(int(sheet.cell_value(row_c, 1)))
#                 if len(str(log)) == 1:
#                     student_log = "0" + log
#                 else:
#                     student_log = log
#
#                 name = str(sheet.cell_value(row_c, 3))
#                 code = class_code + student_log + p
#             except:
#                 print(" row-%s not exist")
#                 continue
#             else:
#                 box["code"] = code
#                 box["name"] = name
#                 box["log"] = int(log)
#                 class_logs[code] = box
#
#         row_a = row_c
#
#     all_logs[class_name] = class_logs
#
# json.dump(all_logs, open("./data/json/all_logs.json", "w", encoding="utf-8"))

# name -> code
# all_logs = json.load(open("./data/json/all_logs.json", "r", encoding="utf-8"))
# result = {}
# for i in range(1, 32):
#     i = str(i)
#     for one_code in list(all_logs[i].keys()):
#         one_name = all_logs[i][one_code]["name"]
#         result[one_name] = one_code
#
# json.dump(result, open("./data/json/candidate_name_code_mapping.json", "w", encoding="utf-8"))

# baisc_info
# result = {}
# for i in range(1, 914):
#
#     print("now process row-%s" % i)
#     try:
#         code = str(sheet.cell_value(i, 1)).replace(".0", "")
#         name = str(sheet.cell_value(i, 2))
#         class_name = str(sheet.cell_value(i, 3)).replace(".0", "")
#         self_intro = str(sheet.cell_value(i, 4))
#         f_enterprise_wish = str(sheet.cell_value(i, 5)).replace(".0", "")
#         s_enterprise_wish = str(sheet.cell_value(i, 6)).replace(".0", "")
#     except IndexError:
#         print(" out of range")
#         continue
#
#     print("  code-%s" % code)
#     result[code] = {
#         "code": code,
#         "name": name,
#         "class": class_name,
#         "selfIntroduction": self_intro,
#         "firstWish": f_enterprise_wish,
#         "secondWish": s_enterprise_wish
#     }
#
# json.dump(result, open("./data/json/candidate_basic_info.json", "w", encoding="utf-8"))

# temp
result = {}
for i in range(1, 112):

    print("now process row-%s" % i)
    try:
        code = str(sheet.cell_value(i, 0)).replace(".0", "")
        name = str(sheet.cell_value(i, 1))
    except IndexError:
        print(" out of range")
        continue

    print("  code-%s" % code)
    result[code] = {
        "code": code,
        "name": name,
        "class": class_name,
        "selfIntroduction": self_intro,
        "firstWish": f_enterprise_wish,
        "secondWish": s_enterprise_wish
    }

json.dump(result, open("./data/json/candidate_basic_info.json", "w", encoding="utf-8"))

# TODO
# - 登分表收集 done
# - 登分表转json class: log: {"log" "name", "code"} done
# - 简历绑定
# - 人脸对比与上传
# - 所有数据绑定并进行确认(一个json总表，按班级分)

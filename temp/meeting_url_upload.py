# 上传会议链接到数据库

import xlrd
from mongodb import MongoDBManipulator
import json

file_name = "./data/腾讯会议链接收集.xls"
sheet = xlrd.open_workbook(file_name).sheet_by_index(1)
mongodb = MongoDBManipulator("172.16.0.6", 27017, "mongouser", "Tx20233428@")
class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
row_a = 1
all_logs = {}
empty_enterprise_code = [59, 60, 61, 70, 81, 82]

for e_i in range(1, 112):

    if e_i in empty_enterprise_code:
        continue

    print("now process com%s" % e_i)
    box = {}
    row_c = 1+e_i
    try:
        com_now = str(int(sheet.cell_value(row_c, 0)))
        com_now = "com%s" % com_now
    except IndexError:
        print(row_c)
    else:
        try:
            url = str(sheet.cell_value(row_c, 3))
            print(url)
        except:
            print(" row-%s not exist")
            continue
        else:
            meeting_room_list = list(mongodb.get_document("interview", "now", {"_id": com_now}, 1))[0]["meetingUrlList"]
            meeting_room_list["tencent"] = url
            mongodb.update_many_documents("interview", "now", {"_id": com_now}, {"meetingUrlList": meeting_room_list})


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

# TODO
# - 登分表收集 done
# - 登分表转json class: log: {"log" "name", "code"} done
# - 简历绑定
# - 人脸对比与上传
# - 所有数据绑定并进行确认(一个json总表，按班级分)

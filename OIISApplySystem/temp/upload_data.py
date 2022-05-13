# author: Lanzhijiang
# date: 2022.4.15


# import json
# import xlrd
#
#
# result = {}
# result_path = "./result.json"
#
#
# for c in range(1, 32):
#     print("now process: class-%s" % c)
#     file_name = "%s.xls" % c
#     sheet = xlrd.open_workbook(file_name).sheet_by_index(0)
#
#     box = {}
#     for row in range(1, 60):
#         try:
#             box["code"] = int(sheet.cell_value(row, 1))
#             box["name"] = sheet.cell_value(row, 2)
#             result[str(row)] = box
#         except:
#             continue
#
#     result["%s" % c] = box
#
# json.dump(result, open(result_path, "w", encoding="utf-8"))


# import memcache
#
# c = memcache.Client(["172.16.0.15:9101"])
# a = [-1, 16, 17, 17, 16, 16, 17, 16, 17, 17, 17, 17, 17, 17, 17, 16, 17, 16, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 16, 17, 17, 16, 17, 17, 17, 17, 16, 17, 16, 16, 22, 19, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 16, 17, 17, 17, 16, 0, 0, 0, 19, 17, 17, 17, 19, 17, 21, 17, 0, 17, 16, 17, 17, 16, 17, 17, 17, 17, 17, 0, 0, 17, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 22, 17, 17, 17, 17, 17, 17, 17]
#
# for i in range(1, len(a)):
#     code = str(i)
#     c.set(code, a[i])
#     print("now_set: %s to %s" % (code, a[i]))
import time

from mongodb import MongoDBManipulator
mongodb = MongoDBManipulator("172.16.0.9", 27017, "mongouser", "Tx20233428@")

a = [-1, 16, 17, 17, 16, 16, 17, 16, 17, 17, 17, 17, 17, 17, 17, 16, 17, 16, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 16, 17, 17, 16, 17, 17, 17, 17, 16, 17, 16, 16, 22, 19, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 16, 17, 17, 17, 16, 0, 0, 0, 19, 17, 17, 17, 18, 17, 21, 17, 0, 17, 16, 17, 17, 16, 17, 17, 17, 17, 17, 0, 0, 17, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 22, 17, 17, 17, 17, 17, 17, 0]

mongodb.add_one_document("interview", "temp", {"_id": 0, "whole_status": a})

for i in range(1, len(a)):
    time.sleep(0.2)
    code = str(i)
    mongodb.add_one_document("interview", "temp", {"_id": i, "data": a[i]})
    print("now_add: %s : %s" % (code, a[i]))






remained_info = [-1, 16, 17, 17, 16, 16, 17, 16, 17, 17, 17, 17, 17, 17, 17, 16, 17, 16, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 16, 17, 17, 16, 17, 17, 17, 17, 16, 17, 16, 16, 22, 19, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 16, 17, 17, 17, 16, 0, 0, 0, 19, 17, 17, 17, 19, 17, 21, 17, 0, 17, 16, 17, 17, 16, 17, 17, 17, 17, 17, 0, 0, 17, 17, 17, 17, 17, 17, 21, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 22, 17, 17, 17, 17, 17, 17, 17]
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
data = []
now_fill_code_id = 1
now_fill_code_remained = 1
for column in range(0, 12):
    column += 1
    data.append([])
    fill_remained = False
    fill_id = False
    if column % 2 == 0:
        # 填写名额的
        fill_remained = True
    else:
        # 填写单位编号的
        fill_id = True
    for row in range(0, 19):
        if fill_id:
            try:
                data[column - 1].append(now_fill_code_id)
                now_fill_code_id += 1
            except IndexError:
                data[column - 1].append("单位不存在")
                now_fill_code_id += 1
        elif fill_remained:
            # print(now_fill_code_remained, remained_info[now_fill_code_remained])
            if now_fill_code_remained in empty_enterprise_code:
                data[column - 1].append(0)
                now_fill_code_remained += 1
            else:
                try:
                    value = remained_info[now_fill_code_remained]
                    data[column - 1].append(value)
                    now_fill_code_remained += 1
                except IndexError:
                    data[column - 1].append(0)
                    now_fill_code_remained += 1

print(data)

row_blocks = """
<tr><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th></tr>
"""
for row in range(0, 19):
    column_blocks = ""
    for c_i in range(0, 12):
        column = data[c_i]
        if c_i % 2 == 0:
            column_blocks = column_blocks + "<td><b>%s</b></td>" % column[row]
        else:
            column_blocks = column_blocks + "<td>%s</td>" % column[row]

    row_blocks = row_blocks + "<tr>" + column_blocks + "</tr>"

print(row_blocks)

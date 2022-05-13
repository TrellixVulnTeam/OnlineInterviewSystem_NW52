# author: Lanzhijiang


### the memcached-whole_status generate
from memcached import MemcachedManipulator

memcache = MemcachedManipulator("172.16.0.15", 9101)

base_num = 17
cold_req_enp = [1, 4, 7, 15, 17, 30, 33, 38, 40, 41, 54, 58, 72, 75, 4, 5, 1, 7]
hot_req_enp = [42, 105, 68, 23, 89, 62, 43, 66]
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
all_codes = list(range(1, 113))
result = [-1]


for i in all_codes:
    if i not in empty_enterprise_code:
        if i in cold_req_enp:
            result.append(base_num-1)
        elif i in hot_req_enp:
            order = hot_req_enp.index(i)
            print(order)
            if 0 <= order <= 1:
                result.append(base_num+5)
            elif 2 <= order <= 4:
                result.append(base_num+4)
            else:
                result.append(base_num+2)
        else:
            result.append(base_num)
    else:
        result.append(0)


print(result)
result[112] = 0
memcache._set("whole_status", result)
# 112 should be 0


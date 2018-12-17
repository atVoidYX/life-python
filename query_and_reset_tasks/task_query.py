import datetime
import json
import os
import time
import sys

# sys.path.append("./dependency/bean.py")
# sys.path.append("./dependency/utils.py")
# from amway_order_check.dependency.beans import *
# from amway_order_check.dependency.utils import *

from dependency.beans import *
from dependency.utils import *

error_temp_file_path = "./out/error_temp_task.txt"
result_file_path = "./out/result.txt"
result_message_file_path = "./out/result_detail.txt"
config_file_path = "./config.json"
username = ""
password = ""
start_date_str = ""
end_date_str = ""
biz_type = ""
business_type = ""


def init():
    global username
    global password
    global start_date_str
    global end_date_str
    global business_type
    res = True
    if os.path.isfile(error_temp_file_path):
        os.remove(error_temp_file_path)
    open(error_temp_file_path, 'w')

    if os.path.isfile(result_file_path):
        os.remove(result_file_path)
    open(result_file_path, 'w')

    if os.path.isfile(result_message_file_path):
        os.remove(result_message_file_path)
    open(result_message_file_path, 'w')

    print("环境清理完成")
    if not os.path.isfile(config_file_path):
        print("配置文件不存在,请补充config.json")
        res = False
    else:
        try:
            with open("./config.json", 'r', encoding='utf-8') as json_file:
                if json_file is not None:
                    model = json.load(json_file)
                    if model is not None and model['username'] != "" and model['password'] != "":
                        print("读取配置文件")
                        username = model['username']
                        password = model['password']
                        start_date_str = model['start_date_str']
                        end_date_str = model['end_date_str']
                        business_type =  model['business_type']

        except Exception as e:
            print(e)
            res = False
    return res


# -----------------清空文件-------------------
if not init():
    print("初始化错误")
    exit()
print("初始化成功")
# -----------------获得cookies----------------
sso_cookies_key = get_sso_cookies(username=username, password=password)
print("sso_key:" + sso_cookies_key)

# ----------------日期模块--------------------
dd = datetime.datetime

date_format = "%Y-%m-%d"

start_date = dd.strptime(start_date_str, date_format)
end_date = dd.strptime(end_date_str, date_format)

temp_date = start_date

date_list = []
while temp_date <= end_date:
    date_list.append(dd.strftime(temp_date, date_format))
    temp_date = temp_date + datetime.timedelta(days=1)

print("日期列表:" + str(date_list))
# ----------------保存错误task任务记录--------------------
try:
    for current_date in date_list:
        res = query_task_data(sso_cookies_key=sso_cookies_key,business_type=business_type, query_date=current_date, query_status=2)
        res = json.loads(res)
        if 0 < res['iTotalRecords'] <= 500:
            print(current_date + "  错误task数量:" + str(res['iTotalRecords']))
            print("原始数据：" + str(res))
            error_task_list = res["aaData"]
            with open(error_temp_file_path, 'a') as fout:
                # fout.writelines(current_date + " error task:\n")
                for error_task in error_task_list:
                    fout.writelines(error_task['bizSeqNo'] + "/" + error_task['part'] + "/" + current_date + "\n")
                    # print(error_task['bizSeqNo'])

            fout.close()
        elif res['iTotalRecords'] > 500:
            print("警告: 单天错误记录超过500条！！,请联系作者优化")
            exit()
        else:
            print(current_date + "  没有错误记录")
except Exception as e:
    print(e)
    exit()
try:
    # ----------------读取原始错误task任务记录进行重试--------------------
    task_list = []
    with open(error_temp_file_path, 'r') as fin:
        read_list = fin.readlines()
        for task_str in read_list:
            temp = task_str.split('/')
            task = TaskErrorRecord(so_no=temp[0], part=temp[1], date=temp[2].replace("\n", ""), status='fail')
            task_list.append(task)
    fin.close()
    # print(task_list)
    print('读取到的失败任务总数：' + str(len(task_list)))

    for i in range(0, len(task_list)):
        res = reset_one_task(sso_cookies_key=sso_cookies_key, task=task_list[i])
        if res != 1:
            print("任务请求发送失败：" + task_list[i].so_no)

    print("全部重置成功，等待10s，重新判定状态")
    time.sleep(5)

    result_list = []
    for i in range(0, len(task_list)):
        res = query_task_data(sso_cookies_key=sso_cookies_key, business_type=business_type,query_date=task_list[i].date,
                              query_so_no=task_list[i].so_no)
        res = json.loads(res)
        print(task_list[i].so_no + "状态:" + ("仍然失败" if res["aaData"][0]['status'] == 2 else "成功"))
        if res["aaData"][0]['status'] == 2:
            err_message = query_error_message(sso_cookies_key=sso_cookies_key, task=task_list[i])
            task = res["aaData"][0]
            result_list.append(task['bizSeqNo'])
            with open(result_file_path, 'a',encoding='utf-8') as fout:
                fout.writelines(task['bizSeqNo'] + "/" + task['part'] + "/" + task_list[i].date + "\n")
                # print(error_task['bizSeqNo'])
            fout.close()
            # 保存详细错误信息
            with open(result_message_file_path, 'a',encoding='utf-8') as fout:
                fout.writelines(task['bizSeqNo'] + "/" + task['part'] + "/" + task_list[i].date + "\n")
                fout.write(err_message+'\n')
                fout.write("+++++++++++++++++++++++++"*3+ '\n\n\n')
            fout.close()
    print("----------------运行结束---------------")
    print("如需查看原始失败订单请查看error_temp_task.txt")
    print("如需查看重置后仍然失败的订单请查看result.txt")
    print("如需查看仍然失败的订单详细信息请查看result_detail.txt")
except Exception as e:
    print(e)
    exit()

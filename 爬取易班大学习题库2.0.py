# -*- coding:utf-8 -*-
from tkinter.tix import Tree
import requests
from Crypto.PublicKey import RSA
import base64
import rsa
import re
import json
import pandas as pd

class YiBan(object):
    def __init__(self):
        self.session = requests.session()

    def login(self, username, rsa_pass, ruleId):  # 登录易班大学习
        try:
            print('正在尝试登录...')
            url = 'https://oauth.yiban.cn/code/usersure'
            data = {
                'oauth_uname': username,
                'oauth_upwd': self.crypto(rsa_pass),
                'client_id': '8486f6909598db9a',
                'redirect_uri': 'http://f.yiban.cn/iapp254007',
                'state': 'STATE',
                'display': 'html',

            }
            response = self.session.post(url, data=data)
            url = 'https://f.yiban.cn/iapp254007'
            response = self.session.get(url)
            token = re.findall(r"var token = \'(.*)';",response.text)[0]
            # print(token)
            print('登陆成功。')
        except:
            print('登录信息有误,请检查。')
        while True:
            self.read_tiku(ruleId, token)

    def crypto(self, password):  # 获取公钥并加密登录密码
        url = 'https://oauth.yiban.cn/code/html?client_id=8486f6909598db9a&redirect_uri=http://f.yiban.cn/iapp254007&state=STATE'
        response = self.session.get(url)
        public_key = re.findall(r"BEGIN PUBLIC KEY-----\sM(.*)-----END PUBLIC KEY", response.text, re.S)[0]
        public_key = '-----BEGIN PUBLIC KEY-----\nM' + public_key + '-----END PUBLIC KEY-----'
        # print(public_key)
        rsa_key = RSA.importKey(public_key)
        crypto = rsa.encrypt(password.encode(), rsa_key)
        rsa_pass = base64.b64encode(crypto).decode()
        # print(rsa_pass)
        return rsa_pass
        
    def read_tiku(self, ruleId, token):
        data = {'ruleId':ruleId}
        header = {'token':token}
        try:
            # 获取测试试卷ID
            url = "http://220.160.52.44:8080/api/mobile/examInfo/beginTest"
            response = self.session.post(url,headers=header,data=data).text
            response = json.loads(response)
            recordId = str(response["data"]["id"])
            # print(response)
        except :
            # 
            url = "http://220.160.52.44:8080/api/mobile/examInfo/checkExam?userAnswer={}"
            response = self.session.get(url,headers=header).text
            response = json.loads(response)
            recordId = response["data"]["recordId"]
            #print(response)

        # 交卷
        url = "http://220.160.52.44:8080/api/mobile/examInfo/submitExam"
        response = self.session.post(url,headers=header,data={"recordId":str(recordId)})
        #查看答题详情
        url = "http://220.160.52.44:8080//api/mobile/examInfo/getRecord?id="
        response = self.session.get(url+str(recordId),headers=header)
        jsondata = response.json()["data"]["detail"]
        self.write_tiku(jsondata)
        #print(jsondata)

    '''
    # 数据清洗
    def write_tiku(jsondata):
        data = pd.DataFrame(jsondata)
        question_id = pd.DataFrame(jsondata)["id"]
        a =0
        for i in range(len(question_id)):
            df = pd.read_csv(r"", usecols=[0])
            #print(df)
            print(question_id[i] not in df)
            if question_id[i] not in df :
                data.to_csv('tiku.csv', mode='a', index=False, columns=["id","answer"], header=False)
                print(question_id[i])

            else:
                a += 1
                print(a)
        # print(df)
    '''


    #数据写入
    def write_tiku(self, jsondata):
        with open('tiku.txt','a+',encoding='utf-8') as f:
            Repetition_rate = 0
            for i in jsondata:
                with open('tiku.txt','r',encoding='utf-8') as tiku:
                    data = tiku.read()
                    if data.find(str(i["id"])) == -1:
                    # print(i["id"],end=" ",file=f)
                        lowercase = i["answer"].lower().strip()
                        #print(lowercase,file=f)
                        # for a in range(int(len(lowercase))):
                        #     print(i["option_" + lowercase[a]],file=f)
                        f.write(str(i["id"])+": \'"+str.upper(lowercase)+"\',")
                        Repetition_rate+=1
                    else:
                        continue
        print("共有"+str(Repetition_rate)+"题被添加进题库")

    def choose(self, number):
        ruleId = 0
        if number == 0:   # 思修
            ruleId = 2
        elif number == 1: # 马哲
            ruleId = 2
        elif number == 2: # 形策
            ruleId = 2
        else :
            print('error, 您输入的有误')
        return ruleId

if __name__ == '__main__':
    yiban = YiBan()
    print("""
    课程代码说明:
    -----------------
    | 选择 0 是 思修 |
    | 选择 1 是 马哲 |
    | 选择 2 是 形策 |
    -----------------
    """)
    username = input('请输入您的账号：') 
    rsa_pass = input('请输入您的密码：') 
    number = input('请输入需要爬取的题库：')
    try:
        yiban.login(username, rsa_pass,yiban.choose(int(number)))
    except SystemExit:
        print('您输入的有误请重新检查')

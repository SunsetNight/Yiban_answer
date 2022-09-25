# -*- coding: utf8 -*-
import requests
from Crypto.PublicKey import RSA
import base64
import rsa
import re
import json

class YiBan(object):
    def __init__(self):
        self.session = requests.Session()

    def login(self, username, password):
        # 获取公钥并加密登录密码
        url = 'https://oauth.yiban.cn/code/html?client_id=8486f6909598db9a&redirect_uri=http://f.yiban.cn/iapp254007&state=STATE'
        response = self.session.get(url)
        public_key = re.findall(r"BEGIN PUBLIC KEY-----\sM(.*)-----END PUBLIC KEY", response.text, re.S)[0]
        public_key = '-----BEGIN PUBLIC KEY-----\nM' + public_key + '-----END PUBLIC KEY-----'
        rsa_key = RSA.importKey(public_key)
        crypto = rsa.encrypt(password.encode(), rsa_key)
        rsa_pass = base64.b64encode(crypto).decode()
        # 登录易班大学习
        try:
            header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50'}
            print('正在尝试登录...')
            url = 'https://oauth.yiban.cn/code/usersure'
            data = {
                'oauth_uname': username,
                'oauth_upwd': rsa_pass,
                'client_id': '8486f6909598db9a',
                'redirect_uri': 'http://f.yiban.cn/iapp254007',
                'state': 'STATE',
                'display': 'html',
            }
            response = self.session.post(url, data=data)
            url = 'https://f.yiban.cn/iapp254007'
            response = self.session.get(url, headers=header)
            token = re.findall(r"var token = '(.*)';",response.text)[0]
            print(token)
            self.session.headers={'token': token}
            print('登陆成功。')
        except:
            print('登录信息有误,请检查。')
        self.submitAnswer()

    def submitAnswer(self):  # 开始答题
        # 获取考试试卷ID
        url = "http://220.160.52.44:8080/api/mobile/examInfo/beginExam"
        recordId = str(json.loads(self.session.post(url, data={'examInfoId': self.choose()}).text)["data"]["id"])
        # 获取考试题库
        url = "http://220.160.52.44:8080/api/mobile/examInfo/getExam?recordId="+recordId
        questionList = json.loads(self.session.get(url).text)['data']['questionList']
        # 开始答题
        print('载入题库...')
        with open ("tiku.txt", "r+", encoding='utf-8') as f :
            tiku = eval(f.read())
            # print(type(tiku))
            dict = {}
            for i in range(len(questionList)):
                answer = tiku[questionList[i]['id']]
                name = "answer_"+str(i+1)
                dict[name] = answer
        dict_json = json.dumps(dict)
        data = {
        'recordId': recordId,
        'userAnswer': dict_json 
        }
        url = "http://220.160.52.44:8080/api/mobile/examInfo/submitExam"
        response = json.loads(self.session.post(url, data=data).text)
        # 考试结果
        url = "http://220.160.52.44:8080//api/mobile/examInfo/getRecord?id="+recordId
        result = json.loads(self.session.get(url).text)['data']['sum_score']
        print(f"您的试卷id:{recordId}，成绩:{result}")

    def choose(self):  # 选择试卷
        url = "http://220.160.52.44:8080/api/mobile/examInfo/getExamList?examType=QP0001"
        response = json.loads(self.session.get(url).text)['data']
        # items = []
        dict = {}
        for i ,item in enumerate(response):
            # items.append(str(i)+'.'+item['name'])
            dict[i] = item['name']
        # print(items)
        print(dict)
        rule_id=int(input('请输入您的选择的课程：'))
        exam_id={str(response[rule_id]['id'])}
        return exam_id


if __name__ == '__main__':
    yiban = YiBan()
    username = input('请输入您的账号：') 
    password = input('请输入您的密码：') 
    yiban.login(username, password)
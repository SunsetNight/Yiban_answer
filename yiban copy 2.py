# -*- coding: utf8 -*-
import requests
from Crypto.PublicKey import RSA
import base64
import rsa
import re
import json

class YiBan(object):
    def __init__(self):
        self.session = requests.session()

    def do(self, username, rsa_pass, exam_id):
        self.login(username, rsa_pass, exam_id)

    def login(self, username, rsa_pass, exam_id):  # 登录易班大学习
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
        self.submitAnswer(exam_id, token)

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

    def submitAnswer(self, exam_id, token):  # 开始答题
        exam_id = exam_id
        header={'token': token}
        # 获取考试试卷ID
        url = "http://220.160.52.44:8080/api/mobile/examInfo/beginExam"
        response = self.session.post(url, headers=header, data={'examInfoId': exam_id}).text
        response = json.loads(response)
        recordId = response["data"]["id"]
        recordId = str(recordId)
        # 获取考试题库
        url = "http://220.160.52.44:8080/api/mobile/examInfo/getExam?recordId="+recordId
        response = self.session.get(url, headers=header).text
        response = json.loads(response)
        questionList = response['data']['questionList']
        # print(questionList)
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
        response = self.session.post(url, headers=header, data=data).text
        response = json.loads(response)
        # 考试结果
        url = "http://220.160.52.44:8080//api/mobile/examInfo/getRecord?id="+recordId
        response = self.session.get(url, headers=header).text
        response = json.loads(response)['data']['sum_score']
        print(f"您的试卷id:{recordId}，成绩:{response}")
        # if response['message'] == 'ok':
        #     print('已完成，如未达到满分请检查题库是否完整')
        # else:
        #     print('未完成，未知错误')

    def choose(self, number):
        exam_id = 0
        if number == 0:   # 思修
            exam_id = 1326
        elif number == 1: # 马哲
            exam_id = 946
        elif number == 2: # 形策
            exam_id = 782
        else :
            print('error, 您输入的有误')
        return exam_id


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
    number = input('请输入您的选择的课程：')
    try:
        exam_id = yiban.choose(int(number))
        yiban.do(username, rsa_pass, exam_id)
    except SystemExit:
        print('您输入的有误请重新检查')
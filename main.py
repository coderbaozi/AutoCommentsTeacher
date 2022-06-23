# -*- coding: utf-8 -*-
import time
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from selenium.webdriver.common.action_chains import ActionChains
import random
import requests
import base64
from PIL import Image
import json

# 只需修改下面三项即可 学号 密码 打卡网址
from selenium.webdriver.support import ui
from webdriver_manager.drivers import chrome

# username = "xxx"
# password = "xxx"
url = "xxx"

# 下面是每次填报的时候几个需要填写的地方，F12找到这些位置的 full XPath

selefpeopleckeck="/html/body/form/div/div[11]/div[3]/div[4]"
prefixTeacher = "/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr["
suffixTeacher = "]/td[2]/a"
prefixScore = "/html/body/form/div/div/span/table/tbody/tr[3]/td/fieldset/table/tbody/tr["
suffixScore = "]/td[6]/input"
prefixSpecialScore = "/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[6]/td[2]/a["
suffixSpecialScore = "]"
Evaluationstatement = ["课堂内容充实，老师授课有条理，有重点，对同学既热情又严格，是各位老师学习的榜样。",
                       "教学内容丰富有效，老师在生活工作中给人的感觉是生活朴素，工作认真负责，是一位好的老师！",
                       "老师答疑认真，对同学们提出的问题能够详尽的解答，态度和蔼，十分有耐心，深得学生好评。",
                       "老师教学风趣，它能用日常生活中的简单例子来解释说明课程中的一些专有名词和概念。",
                       "老师对待教学认真负责，语言生动，条理清晰，对待学生严格要求,使课堂气氛比较积极热烈",
                       "老师教学认真，课堂效率高，整节课学下来有收获、欣喜，使人对此门课程兴趣浓厚。",
                       "老师授课认真，细致，能充分利用时间，老师讲课时的激情会感染我们，课堂气氛很好。",
                       "老师授课时重点突出，充分利用黑板推理，演算比较清晰，易于让学生接受的特点。"]
TeacherPositionList=[]

#验证码识别
def do_captcha():
    # encoding:utf-8

    '''
    通用文字识别（高精度版）
    '''

    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    # 二进制方式打开图片文件
    f = open('captcha.png', 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    access_token = 'xxx'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        print(response.json())
        return response.json()

#循环评教
def do_Dealcomments():
    # 循环执行评教
    num = 1
    while (num < 13):
        num += 1
        everyTeacherPosition = prefixTeacher + str(num) + suffixTeacher
        TeacherPositionList.append(everyTeacherPosition)
        if num == 6:
            temp=0
            while (temp<2):
                temp+=1
                everyTeacherPosition=prefixSpecialScore+str(temp)+suffixSpecialScore
                TeacherPositionList.append(everyTeacherPosition)

def do_comments(driver,everyTeacherPosition):
        # 保存原始的浏览器窗口
        initialWindowHandle = driver.current_window_handle;
        # 转换ifram
        driver.switch_to.frame('zhuti')
        # 点击进入评教新窗口
        driver.find_element_by_xpath(everyTeacherPosition).click();
        # # 保存完成切换句柄
        # driver.switch_to.window(initialWindowHandle)
        driver.switch_to.default_content()
        # 获取所有窗口句柄
        windows1 = driver.window_handles
        # # 切换句柄,切换dao最新打开的窗口
        driver.switch_to.window(windows1[-1])
        # 输入分数,输入评价语句
        start = 1
        while (start < 7):
            start += 1
            # 随机老师的分数
            everyScore = random.randint(95, 100)
            everyTeacherScore = prefixScore + str(start) + suffixScore
            driver.find_element_by_xpath(everyTeacherScore).send_keys(everyScore)

        # 随机老师评价搞一个数组来随机读取一个评价？
        EvaluationstatementImpl = Evaluationstatement[random.randint(0, 7)]
        driver.find_element_by_xpath('/html/body/form/div/div/span/table/tbody/tr[5]/td/textarea').send_keys(
            EvaluationstatementImpl)
        # 点击保存
        driver.find_element_by_xpath('/html/body/form/div/div/div[2]/em/span[2]/input[1]').click()
        # 确定弹回
        driver.switch_to.alert.accept()
        driver.switch_to.window(windows1[0])

#模拟登陆打卡
def do_login(driver):
    try:
        #driver.switch_to.frame('my_toprr')
        # 将窗口最大化
        driver.maximize_window()
        # 找到登录框 输入账号密码
        # driver.find_element_by_name('txtUserName').send_keys(username)
        driver.find_element_by_xpath('/html/body/form/div/div[3]/dl[2]/dd/input[1]').click()
        # driver.find_element_by_xpath('/html/body/form/div/div[3]/dl[2]/dd/input[2]').send_keys(password)
        #处理验证码
        captcha=driver.find_element_by_id('icode')
        captcha.screenshot('capt.png')
        img=Image.open('capt.png')
        img = img.convert('L')  # P模式转换为L模式(灰度模式默认阈值127)
        count = 160  # 设定阈值
        table = []
        for i in range(256):
            if i < count:
                table.append(0)
            else:
                table.append(1)

        img = img.point(table, '1')
        img.save('captcha.png')  # 保存处理后的验证码
        captchaJson=do_captcha()
        print(captchaJson['words_result'][0])
        #找到验证码框并输入验证码
        driver.find_element_by_name('txtSecretCode').send_keys(captchaJson['words_result'][0]['words'])
        time.sleep(8)
        driver.find_element_by_name('Button1').click()  # 点击登录

        # 延时两秒
        time.sleep(2)


        #鼠标悬停进入评教页面
        #定位触发隐藏元素显示的位置，就是设置按钮，如下所示
        mouse = driver.find_element_by_xpath('/html/body/div/div[1]/ul/li[7]/a/span')
        #鼠标移动到触发点
        ActionChains(driver).move_to_element(mouse).perform()
        #定位隐藏元素
        driver.find_element_by_xpath('/html/body/div/div[1]/ul/li[7]/ul/li/a').click()

        # first="/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/a"
        # sexond="/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[3]/td[2]/a"
        # third="/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[4]/td[2]/a"
        # "/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[6]/td[2]/a[1]"
        # "/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[6]/td[2]/a[2]"
        # "/html/body/form/div/div/span/table/tbody/tr[3]/td/table/tbody/tr[13]/td[2]/a"



        #暴力提交
    except Exception as e:
        print("出现错误了", e)


def send_email():
    # 设置服务器所需信息
    # qq邮箱服务器地址
    mail_host = 'smtp.qq.com'
    # qq用户名
    mail_user = '你的邮箱'
    # 密码(部分邮箱为授权码)
    mail_pass = '申请的授权码'
    # 邮件发送方邮箱地址
    sender = '发送者邮箱'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = ['接受者邮箱']

    # 设置email信息
    # 邮件内容设置
    message = MIMEText('今日份打卡成功！！！', 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = '自动化打卡成功'
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host)
        # 连接到服务器
        smtpObj.connect(mail_host, 465)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        print('发送邮件成功')
    except smtplib.SMTPException as e:
        print('发送邮件失败', e)


if __name__ == '__main__':
    # 模拟浏览器打开网站
    driver = webdriver.Chrome()
    driver.get(url)
    # 登录并打卡
    #你有30s输入账号和密码
    time.sleep(30)
    do_login(driver)
    do_Dealcomments()
    count=0
    while(count<13):
        do_comments(driver,TeacherPositionList[count])
        count+=1
    # 给邮箱发送邮件
    #send_email()
    # 暂时不发邮件
    print("打卡结束")
    time.sleep(60)  # 终端给你时间确认已经打卡成功
    driver.quit()

from selenium import webdriver
from aip import AipOcr
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import schedule
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
url = 'https://cw.jnu.edu.cn/Main.aspx'

def send_email(sender, email_keys, receiver,text):#所需参数：发件人账号、秘钥，收件人账号
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = formataddr(["FromRunoob", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr(["FK", receiver])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = text  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
    server.login(sender, email_keys)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(sender, [receiver, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接

def get_file_content():
    with open('./code.png', 'rb') as fp:
        return fp.read()

# 获取验证码
def get_caiwu(account, key, APP_ID,API_KEY ,SECRET_KEY ):#所需参数：账号、密码
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    code_href = browser.find_element_by_id('imgCheckCode').get_attribute("src")
    print(str(code_href))
    # 此处切换句柄，在新界面打开验证码页面，避免关掉当前页面、验证码更换
    browser.execute_script("window.open();")
    browser.switch_to_window(browser.window_handles[1])
    browser.get(code_href)
    # 移动句柄，对新打开页面进行操作
    browser.get(code_href)
    browser.get_screenshot_as_file('./code.png')

    # 调用通用文字识别（高精度版） """
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    image = get_file_content()
    code_ocr_original_result = client.basicAccurate(image)
    words_result = code_ocr_original_result['words_result']
    code_num = int(words_result[0]['words'])
    browser.switch_to_window(browser.window_handles[0])

    browser.find_element_by_xpath('/html/body/form/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[2]/input').send_keys(account)
    browser.find_element_by_xpath('/html/body/form/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[2]/input[1]').send_keys(key)
    browser.find_element_by_xpath('/html/body/form/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[2]/div/input').send_keys(code_num)
    browser.find_element_by_xpath('/html/body/form/div[5]/div[1]/div[2]/div[2]/input[1]').click()

    time.sleep(5)
    browser.find_element_by_xpath('/html/body/form/div[4]/div[1]/div/div[6]').click()
    time.sleep(5)
    browser.find_element_by_xpath('/html/body/form/div[4]/div[1]/div/div[7]/ul/ul[1]/li[1]/a').click()
    time.sleep(5)
    try:
        money = browser.find_element_by_xpath('/html/body/form/div[8]/div/table/tbody/tr/td[3]/ul/li[1]/label')
        text = '发钱了^.^'
        send_email(sender,email_keys,receiver,text)
    except:
        text = '没发钱'
        send_email(sender, email_keys, receiver, text)
    browser.quit()

#设置邮箱信息（发件人、收件人
sender = '@qq.com'  # 发件人邮箱账号
email_keys = ''  # 发件人邮箱秘钥
receiver = '@qq.com'  # 收件人邮箱账号
#设置财务处账号密码
account = ''
key = '!'

# 百度api是我自己的，以后换掉
APP_ID = '24527583'
API_KEY = ''
SECRET_KEY = ''

#以下是设定查询时间，这里设置一天查询三次：早上8点，中午12点半，晚上9点
#还没发钱就放弃吧
schedule.every().day.at("08:00").do(get_caiwu,account, key, APP_ID,API_KEY ,SECRET_KEY )
schedule.every().day.at("12:30").do(get_caiwu,account, key, APP_ID,API_KEY ,SECRET_KEY )
schedule.every().day.at("21:00").do(get_caiwu,account, key, APP_ID,API_KEY ,SECRET_KEY )
while True:
    schedule.run_pending()   # 运行以上任务




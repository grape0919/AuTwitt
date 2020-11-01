from PyQt5.QtCore import QDateTime
from openpyxl import load_workbook
import random
import os

import tweepy


class HeadOfBlogger:

    postThread = None
    countDownUI = None

    def __init__(self, countDownUI):
        self.countDownUI = countDownUI

    def readExcelFile(self, filepath):
        print("Blogger read excel")
        load_wb = load_workbook(filepath)
        #시트 이름으로 불러오기
        for load_ws in load_wb:
            # load_ws = load_wb['문단']
            mylist = [ [c.value for c in r]  for r in load_ws ]
            self.phList = list(map(list, zip(*mylist)))
            break

        self.isLoaded = True

    def makeArticle(self):
        if(self.isLoaded):
            result = []
            for phs in self.phList:
                temp = None
                while(temp==None):
                    temp = random.choice(phs)

                result.append(temp)
            return result
        else:
            print("문단 엑셀 파일을 먼저 불러오세요.")
            return None

    def setDate(self, qDateTime, period):
        self.datetime = qDateTime
        self.period = period*60


    def postArticle(self):
        self.running = True

        try:
            self.postThread = threading.Thread(target=self.postingThread, args=())

            self.postThread.start()
        except:
            return (False, "포스팅 시작에 실패하였습니다. \n 지속적으로 오류 발생시 개발자에게 문의하세요. \n ghdry2563@gmail.com")

        return None

    def postingThread(self):
        print("Blogger start posting")
        while(self.running):
            gap = self.datetime.secsTo(QDateTime.currentDateTime())
            countDown = self.period-(gap%self.period)
            self.countDownUI.setText(str(countDown))
            if(gap < 0):
                time.sleep(1)
                continue
            elif(gap >= 0):
                temp = gap%self.period
                if(temp > 0):
                    time.sleep(1)
                    continue
                elif(temp == 0):
                    time.sleep(5)
                    self.post()

class ApiBlogger(HeadOfBlogger):

    # headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
    APP_ID = ""
    SECRET_KEY = ""
    REDIRECTION_URL = "http://"
    isLoaded=False
    ACCESS_TOKEN = ""

    auth = None

    def setProp(self, prop):
        self.APP_ID = prop.app_id
        self.SECRET_KEY = prop.scrt_key

    def getKeyUrl(self):
        self.auth = tweepy.OAuthHandler(self.APP_ID, self.SECRET_KEY)
        try:
            self.REDIRECTION_URL = self.auth.get_authorization_url()
            print("key url : "+self.REDIRECTION_URL)
            return self.REDIRECTION_URL
        except:
            print("KEY, SECRET_KEY 가 잘못 입력되었습니다.")
            return False



    def getToken(self, key):
        print("getToken")
        self.token = self.auth.get_access_token(key)
        self.auth.set_access_token(self.token[0], self.token[1])
        try:
            self.api = tweepy.API(self.auth)
            return True
        except:
            return False
    
    def post(self):
        imgFolderPath = os.getcwd()+"\\img"
        img_file_list = os.listdir(imgFolderPath)
        imgFilePath = imgFolderPath+"/"+random.choice(img_file_list)
        article = self.makeArticle()
        if(article is not None):
            a = "\n".join(article)
            self.api.update_with_media(imgFilePath, status=a)
            

from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
import time
import threading

class SeleniumBlogger(HeadOfBlogger):

    url = ""
    id = ""
    passwd = ""

    running = False
    datetime = None
    period = 0

    def __init__(self, countDownUI):        
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
        options = wb.ChromeOptions()
        # options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        self.driver = wb.Chrome(executable_path='lib/chromedriver.exe', chrome_options=options)
        self.driver.implicitly_wait(10)

        super().__init__(countDownUI)

    def login(self):
        try:        
            self.driver.get("https://twitter.com/login")#self.url + "manage/entry/post")
            # self.driver.find_element_by_name("link_tistory_id").click()
            self.driver.find_element_by_name("session[username_or_email]").send_keys(self.id)
            self.driver.find_element_by_name("session[password]").send_keys(self.passwd)

            self.driver.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div[1]/form/div/div[3]/div").click()
            return True
        except:
            return False

    def setProp(self, prop):
        
        self.url = prop.url
        if(self.url.endswith(".com")):
            self.url += "/"


        self.id = prop.id
        self.passwd = prop.passwd
                    
    def post(self):
        article = self.makeArticle()
        if(article is not None):
            self.driver.get("https://twitter.com/compose/tweet")#self.url + "manage/entry/post")
            try:
                time.sleep(1)
                alert = self.driver.switch_to.alert
                alert.dismiss()
            except:
                print("alert 창 없음")

            # self.driver.find_element_by_class_name("textarea_tit").send_keys(article[0])
            
            # iframes = self.driver.find_elements_by_tag_name('iframe')

            imgFolderPath = os.getcwd()+"\\img"

            for idx in range(0,len(article)):
                # if(article[idx] == "<img>"):
                #     img_file_list = os.listdir(imgFolderPath)
                #     imgFilePath = imgFolderPath+"/"+random.choice(img_file_list)
                #     self.driver.find_element_by_id("mceu_0-open").click()
                #     self.driver.find_element_by_id("mceu_32").click()
                #     #find_element_by_css_selector("input[name='filePath'][type='file']")
                #     self.driver.find_element_by_id("openFile").send_keys(imgFilePath)
                #     self.driver.switch_to_frame(iframes[0])
                #     self.driver.find_element_by_id("tinymce").send_keys(Keys.ENTER)
                #     self.driver.switch_to_default_content()

                # else:
                # self.driver.switch_to_frame(iframes[0])
                print(article[idx])
                self.driver.find_element_by_xpath("/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[3]/div/div/div/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div").send_keys(article[idx])
                self.driver.find_element_by_xpath("/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[3]/div/div/div/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div").send_keys(Keys.ENTER)
                # self.driver.switch_to_default_content()
                
            time.sleep(5)

            self.driver.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div[2]/div/div/div/div[3]/div").click()

            time.sleep(10)
            # self.driver.find_element_by_xpath("/html/body/div[7]/div/div/div/form/fieldset/div[3]/div/button[2]").click()

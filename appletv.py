from datetime import *
import time
from os import system
import requests
import pymongo
from selenium.webdriver.common import keys 
#from mongo.connection import MongoDB
import simplejson as json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class AppleTV():
    def __init__(self):
        print("HOLA")
        #self.db = MongoDB()
        self.url = 'https://tv.apple.com/hh'
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.scraping()
        self.coutries_code = []
        
    def scraping(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div"))).click()
        time.sleep(2)
        elem = self.driver.find_element_by_class_name('locale-switcher-banner__dropdown__copy')
        elem.send_keys(Keys.DOWN)
        time.sleep(1)
        elem.send_keys(Keys.ENTER)
        
        time.sleep(2000)
if __name__ =='__main__':
    AppleTV()
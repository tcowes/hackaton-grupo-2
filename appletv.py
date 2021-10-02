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
        self.start_url = 'https://tv.apple.com/hh'
        self.main_url = 'https://tv.apple.com/'
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.scraping()
        
        
    def scraping(self):
        countries = self.get_countries_codes()
        for country in countries:
            self.driver.get(self.main_url + country)
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[1]/div/div[2]/div/div/button')))
            scheight = .1
            while scheight < 9.9:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
                scheight += .01
            html = self.driver.page_source  
            soup = BeautifulSoup(html, "html.parser")
            all_divs = soup.find_all("div",class_="shelf-grid")
            top_series = []
            top_movies = []
            top_kids = []
            category_identificator = {
                "Drama Series": "ember52",
                "Comedy Series": "ember61",
                "Non-Fiction Series": "ember65",
                "Feature Films": "ember67"
            }
            category_id_list = "ember52", "ember61", "ember65", "ember67"

            for div in all_divs:
                category = div.find("h2",class_="typ-headline-emph")
                try:
                    category_id = category["id"]
                except:
                    continue
                category_name = div.find("h2",class_="typ-headline-emph").text.strip()
                if category_id in category_id_list:
                    dirty_elements = div.find("ul",class_="shelf-grid__list")
                    clean_elements = dirty_elements.find_all("li",class_="shelf-grid__list-item")
                    for element in clean_elements:
                        try:
                            element_div = element.find("div",class_="canvas-lockup")
                            if element_div:
                                title = element_div["aria-label"]
                                print(title)
                                info = element_div["data-metrics-click"]
                                info = info.replace("{","")
                                info = info.replace("}","")
                                info = info.split(",")
                                deeplink = info[2].replace("actionUrl","")
                                deeplink = deeplink.replace('"',"")
                                deeplink = deeplink.replace(":","")
                                deeplink = "https://" + deeplink.replace("https//","")
                                picture = element_div.picture
                                for picture_element in picture:
                                        print(picture_element)
                        except:
                            pass

            
    def get_countries_codes(self):
        countries_codes = []
        self.driver.get(self.start_url)
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div"))).click()
        time.sleep(2)
        elem = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]")
        time.sleep(1)
        elem.send_keys(Keys.DOWN)
        time.sleep(1)
        elem.send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/button").click()
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        all_a = soup.find_all("a",class_="locale-switcher-modal__list__item")
        for a in all_a:
            code = a["href"]
            code = code.replace("/","")
            countries_codes.append(code)
        
        return countries_codes

if __name__ =='__main__':
    AppleTV()
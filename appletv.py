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
        #self.db = MongoDB()
        self.start_url = 'https://tv.apple.com/hh'
        self.main_url = 'https://tv.apple.com/'
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        #options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.currentSession = requests.session()
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.scraping()
        
    def scraping(self):
        countries = self.get_countries_codes()
        scraped_countries = []
        pre_data = []
        for x, country in enumerate(countries):
            print("---------- Analizando Top Ten en " + country["Country"] + ". País " + str(x+1) + " de " + str(len(countries)) + " ----------")
            self.driver.get(self.main_url + country["Code"])
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
                "ember52": "Drama Series",
                "ember59": "Comedy Series",
                "ember65": "Feature Films",
                "ember71": "Non-Fiction Series",
                "ember77": "Family Fun"
            }
            category_id_list = "ember52", "ember59", "ember65", "ember71", "ember77"
            
            for data in all_divs:
                category = data.find("h2",class_="typ-headline-emph")
                try:
                    category_id = category["id"]
                except:
                    continue
                if category_id in category_id_list:
                    list_of_li = data.find_all("li",{"class":"shelf-grid__list-item"})
                    # print(list_of_li)
                    for li in list_of_li:
                        div = li.find('div',{'class': 'canvas-lockup'})
                        if not div:
                            continue
                        if not div.get('data-metrics-click'):
                            continue
                        data= div.get('data-metrics-click')
                        data= json.loads(data) 
                        index = int(li["data-item-index"]) + 1
                        id= data['targetId']
                        #print(index)
                        #print(id)
                        payload = {
                            'Id': id,
                            'Country': country["Country"],
                            'Category': category_identificator[category_id],
                            'Index': index
                        }
                        pre_data.append(payload)
                    for li in list_of_li:
                        div= li.find('a',{'class': 'notes-lockup'})
                        if not div:
                            continue
                        if not div.get('data-metrics-click'):
                            continue
                        data= div.get('data-metrics-click')
                        data= json.loads(data) 
                        index = int(li["data-item-index"]) + 1
                        #print(index)
                        id= data['targetId']
                        #print(id)
                        payload = {
                            'Id': id,
                            'Country': country,
                            'Category': category_identificator[category_id],
                            'Index': index
                        }
                        pre_data.append(payload)
            self.get_metadata(pre_data)
            
    def get_metadata(self, pre_data):
        print("..... Cruzando datos con APIs para extraer más metadata ......")
        print("Pre Data:")
        for element in pre_data:
            print(element)
            url = 'https://tv.apple.com/api/uts/v2/view/show/{}?utsk=6e3013c6d6fae3c2%3A%3A%3A%3A%3A%3A235656c069bb0efb&caller=web&sf=143441&v=36&pfm=web&locale=en-US'.format(element["Id"])
            print(url)
            response = self.getUrl(url=url)
            try:
                data = response.json()
            except:
                continue
            content_deeplink = data['data']['content']['url']
            print("content deeplink",content_deeplink)

                        
    def get_countries_codes(self):
        countries = []
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
        all_codes = []
        for a in all_a:
            code = a["href"]
            code = code.replace("/","")
            code = code[:2]
            if code not in all_codes:
                all_codes.append(code)
                country_code = {
                    "Code": code,
                    "Country": a.text.strip()
                }

                countries.append(country_code)
        
        return countries

    def getUrl(self, url):
        requestsTimeout = 5
        while True:
            try:
                response = self.currentSession.get(url, timeout=requestsTimeout)
                return response
            except requests.exceptions.ConnectionError:
                print("Connection Error, Retrying")
                time.sleep(requestsTimeout)
                requestsTimeout = requestsTimeout + 5
                if requestsTimeout == 45:
                    print('Timeout has reached 45 seconds.')
                    break
                continue
            except requests.exceptions.RequestException:
                print('Waiting...')
                time.sleep(requestsTimeout)
                requestsTimeout = requestsTimeout + 5
                if requestsTimeout == 45:
                    print('Timeout has reached 45 seconds.')
                    break
                continue
        

if __name__ =='__main__':
    AppleTV()
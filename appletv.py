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
                            'Country': country["Code"],
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
            deeplink = data['data']['content']['url']
            content_deeplink_data = self.currentSession.get(deeplink).text
            content_soup = BeautifulSoup(content_deeplink_data, 'lxml')
            deeplink = deeplink.replace("https://tv.apple.com/us", "https://tv.apple.com/" + element["Country"])
            if data['data']['content']['type'] == 'Movie':
                type = 'movie'
            elif data['data']['content']['type'] == 'Show':
                type = 'serie'
                seasons = []
                seasons_year ={}
                seasons_ids  = {}
                season_episodes ={}
                skip = 0

                while True:
                    epiurl = 'https://tv.apple.com/api/uts/v2/view/show/{}/episodes?skip={skip}&count=50&utsk=6e3013c6d6fae3c2%3A%3A%3A%3A%3A%3A235656c069bb0efb&caller=web&sf=143441&v=36&pfm=web&locale=en-US'.format(element["Id"], skip=skip)
                    print('URL EPISODE ',epiurl)
                    response = self.getUrl(url=epiurl)
                    epidata = response.json()
                    scraped = []
                    for epi in epidata['data']['episodes']:
                            # print(epi)
                            ### ### ### ### ### ### ### ### ### ### 
                            
                            if epi['id'] in scraped:
                                continue
                            else:
                                scraped.append(epi['id'])
                            ### ### ### ### ### ### ### ### ### ###
                            
                            try:             
                                _timestamp = epi['releaseDate']
                                _timestamp = str(_timestamp)
                                _timestamp = _timestamp[:-3]
                                _timestamp = int(_timestamp)
                                year = date.fromtimestamp(_timestamp)
                                year = str(year)
                                year = year.split('-')
                                year = int(year[0])
                                if year < 1870 or year > datetime.now().year:
                                    year = None
                            except:
                                year = None

                            if epi['seasonNumber'] not in [ s["Number"] for s in seasons]:
                                season_episodes[str(epi['seasonNumber'])] = 1
                                seasons.append({'Title': "{}: Season {}".format(epi['showTitle'] ,epi['seasonNumber']), "Number": epi['seasonNumber']})
                            else:
                                season_episodes[str(epi['seasonNumber'])] += 1
                                
                    epiTotal = len(epidata['data']['episodes'])
                                
                    for season in seasons:
                        season['Episodes'] = season_episodes[str(epi['seasonNumber'])]
                        
                    if epiTotal == 50:
                        skip = skip + 50
                    else:
                        break


                if data['data']['content'].get('genres'):
                    genres = []
                for g in data['data']['content']['genres']:
                    genres.append(g['name'])
                else:
                    genres = None
                    
                roles_data = content_soup.find_all("div", {"class": "profile-lockup__details"})
                cast, directors, crew = self.get_roles(roles_data)    
                    
                imageL = []
                images =  data['data']['content']['images']['coverArt']['url'] if data['data']['content']['images'].get('coverArt') else None
                width  =  data['data']['content']['images']['coverArt']['width'] if data['data']['content']['images'].get('coverArt') else None
                height =  data['data']['content']['images']['coverArt']['height'] if data['data']['content']['images'].get('coverArt') else None
                if images != None and width != None and height != None:
                    images = images.split('{')
                    images = images[0]
                    images = images + str(width) + 'x' + str(height) + 'tc.jpg'
                    imageL.append(images)
                try:             
                    _timestamp = data['data']['content']['releaseDate']
                    _timestamp = str(_timestamp)
                    _timestamp = _timestamp[:-3]
                    _timestamp = int(_timestamp)
                    date_ = date.fromtimestamp(_timestamp)
                    year = date.fromtimestamp(_timestamp)
                    year = str(year)
                    year = year.split('-')
                    year = int(year[0])
                    if year < 1870 or year > datetime.now().year:
                        year = None
                except:
                    year = None
                
                if not year:
                    year = self.get_year_from_soup(content_soup)
            
                more_data = data['data']['content']            
                is_original= more_data['isAppleOriginal']
                if more_data.get('rating'):
                    rating = more_data['rating']['displayName'] 
                else:
                    rating = None
                if more_data.get('duration'):
                    duration = more_data['duration'] // 60
                else:
                    duration = None
                
                try:
                    synopsis = more_data['data']['content']['description']
                except:
                    synopsis = None
                    
                if type == "serie":
                    payload = {
                        "platform.name": "AppleTV",
                        "platform.country": element["Country"],
                        "id": element["Id"],
                        "title": data['data']['content']['title'],
                        "year": year,
                        "deeplink_web": deeplink,
                        "synopsis": synopsis,
                        "image": imageL,
                        "rating": rating,
                        "genres": genres,
                        "cast": cast,
                        "directors": directors,
                        "is_original": is_original,
                        "seasons": seasons,
                        "crew": crew
                }
            else:
                payload = {
                        "platform.name": "AppleTV",
                        "platform.country": element["Country"],
                        "id": element["Id"],
                        "title": data['data']['content']['title'],
                        "year": year,
                        "duration": duration,
                        "deeplink_web": deeplink,
                        "synopsis": synopsis,
                        "image": imageL,
                        "rating": rating,
                        "genres": genres,
                        "cast": cast,
                        "directors": directors,
                        "is_original": is_original,
                        "crew": crew
                }
            
            print(payload)
                
                        
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

    def clean_cast(self, cast_list):
        """Limpia los nombres de los actores en caso de ser necesario
        """
        cast = []
        for actor in cast_list:
            cast.append(actor.replace('\xa0', ' '))
        return cast if cast else None

    def get_roles(self, roles_data):
        
        cast = []
        directors = []
        crew = []
        
        for person_data in roles_data:
            person_name_data = person_data.contents[1].text
            person_name = person_name_data.replace('\n','').strip().replace('\xa0', ' ')
            
            role_data = person_data.parent
            person_role = json.loads(role_data['data-metrics-click'])['contentType']
            
            if person_role == 'Actor':
                cast.append(person_name)
                
            elif person_role == 'Director':
                directors.append(person_name)
            
            else:
                crew.append(
                    {'Role': person_role,
                     'Name': person_name})
        
        return cast or None, directors or None, crew or None

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
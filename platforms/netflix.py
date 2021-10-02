import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class Netflix():
    def __init__(self):
        # bbdd:
        self.skippedTitles = 0
        self.skippedEpis = 0
        self.url = 'https://www.netflix.com/'
        self.kids_url = 'https://www.netflix.com/Kids'
        self.content_url = 'https://www.netflix.com/latest?jbv='
        self.driver = webdriver.Firefox()
        self.content = []
        self.epis = []

        self._scraping()
    
    def _scraping(self):
        self.login()
        ids = self.extract_ids()
        if not ids:
            raise AssertionError('--- NO PUDIERON SCRAPEARSE IDS MOST WATCHED ---')
        else:
            content = self.extract_data(ids)
            for content in content:
                print(content)

        WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='previewModal-close']"))).click()
        kids = self.driver.find_element_by_xpath("//a[@href='/Kids']")
        self.driver.execute_script("arguments[0].click();", kids)
        
        time.sleep(4)
        ids = self.extract_ids()
        if not ids:
            raise AssertionError('--- NO PUDIERON SCRAPEARSE IDS KIDS MOST WATCHED ---')
        else:
            content = self.extract_data(ids)
            for content in content:
                print(content)

    def extract_ids(self):
        ''' Extract ten principals contents ids '''

        parameters = []
        WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='/latest']"))).click()
        time.sleep(2)
        ten_contents = self.driver.find_element_by_css_selector(
                "div[data-list-context='mostWatched']").find_elements_by_css_selector(
                    "div[class='title-card-container ltr-0']")
        for content in ten_contents:
            pre_id = content.find_element_by_css_selector(
                    "a[class='slider-refocus']").get_attribute('href')
            clean_id = re.search('watch/(.*)?tctx', pre_id)
            if clean_id:
                parameter = clean_id.group(1).replace('?', '')
                parameters.append(parameter)
            else:
                continue

        return list(set(parameters))

    def extract_data(self, ids):
        ''' Extract all data of contents '''

        for _id in ids:
            url = self.content_url+_id
            self.driver.get(url)
            time.sleep(5)
            title = self.driver.find_element_by_css_selector(
                    "div[class='about-header']")
            data = self.driver.find_element_by_css_selector(
                    "div[class='about-container']")
            content = {}
            content['id'] = _id
            content['title'] = title.find_element_by_tag_name('h3').find_element_by_tag_name('strong').text
            content['url'] = url
            content['year'] = self.driver.find_element_by_css_selector(
                    "div[class='year']").text
            content['synopsis'] = self.driver.find_element_by_css_selector(
                    "p[class='preview-modal-synopsis previewModal--text']").text
            content['rating'] = self.driver.find_element_by_css_selector(
                    "span[class='maturity-number']").text
            try:
                episode_selector = self.driver.find_element_by_css_selector(
                    "div[class='episodeSelector-dropdown']").click()
                episode_selector.find_element_by_css_selector(
                    "button[class='dropdown-toggle ltr-111bn9j']").click()
                dropdown = episode_selector.find_elements_by_css_selector(
                    "li[data-uia='dropdown-menu-item']")
                content['seasons'] = []
                for data in dropdown:
                    content['seasons'].append({'Season': data.find_element_by_css_selector(
                    "div[class='episodeSelector--option']").text, 'Episodes': data.find_element_by_css_selector(
                    "span[class='episodeSelector--option-label-numEpisodes']").text})
            except:
                # ACA QUEDE TOMIIIIIIIIII
                pass
            try:
                content['duration'] = self.driver.find_element_by_css_selector(
                    "span[class='duration']").text
            except NoSuchElementException:
                content['duration'] = None 
            try:
                self.driver.find_element_by_css_selector(
                        "div[class='episodeSelector-season-name']")
                content['type'] = 'serie'
            except NoSuchElementException:
                content['type'] = 'movie'
            try:
                pre_directors = data.find_element_by_css_selector(
                        "div[data-uia='previewModal--tags-person']").find_elements_by_tag_name('a')
                content['directors'] = [name.text.replace(',', '') for name in pre_directors]
            except NoSuchElementException:
                content['directors'] = None
            try:
                names_data = data.find_elements_by_css_selector(
                    "div[data-uia='previewModal--tags-person']")
                if len(names_data) == 3:
                    pre_cast = names_data[2].find_elements_by_tag_name('a')
                    content['cast'] = [name.text.replace(',', '') for name in pre_cast]
                elif len(names_data) == 2:
                    pre_cast = names_data[1].find_elements_by_tag_name('a')
                    content['cast'] = [name.text.replace(',', '') for name in pre_cast]
                else:
                    content['cast'] = None
            except NoSuchElementException:
                content['cast'] = None
            except IndexError:
                content['cast'] = None
            try:
                pre_genres = data.find_element_by_css_selector(
                    "div[data-uia='previewModal--tags-genre']").find_elements_by_tag_name('a')
                content['genres'] = [genre.text.replace(',', '') for genre in pre_genres]
            except NoSuchElementException:
                content['genres'] = None
            
            yield content

    def build_payload(self, content, is_epi=False):
        '''Builds payload depending type'''

        # Indica si el payload a completar es un episodio:
        if is_epi:
            self.is_epi = True
        else:
            self.is_epi = False

        payload = {}
        payload['PlatformCode'] = self._platform_code
        payload['Id'] = content['id']
        payload['Title'] = content['title']
        payload['OriginalTitle'] = None
        #payload['CleanTitle'] = _replace(payload['Title'])
        payload['Type'] = content['type'] if content.get('type') else None
        payload['Seasons'] = content['seasons'] if content.get('seasons') else None

        # En el caso que sea episodio, se agregan y quitan estos campos:
        if self.is_epi:
            payload["ParentTitle"] = self.check_title(content['parent_title'])
            payload["ParentId"] = content['parent_id']
            payload["Season"] = self.check_season(content['season'])
            payload["Episode"] = self.check_number(content['number'])
            del payload["OriginalTitle"]
            del payload['CleanTitle']
            del payload['Type']
            del payload['Seasons']

        payload['Year'] = self.check_year(content['year']) if content.get('year') else None
        payload['Duration'] = int(content['duration']) if content.get('duration') else None
        payload['ExternalIds'] = None  
        payload['Deeplinks'] = {"Web": content['url'], "Android": None, "iOS": None}
        payload['Synopsis'] = self.check_synopsis(content['synopsis']) if content.get('synopsis') else None
        payload['Image'] = [content['image']]
        payload['Rating'] = content['rating']
        payload['Provider'] = [content['provider']]    
        payload['Playback'] = None
        payload['Genres'] = self.check_genres(content['genres'])
        payload['Cast'] = self.check_cast(content['cast']) if content.get('cast') else None
        payload['Crew'] = None
        payload['Directors'] = self.check_director(content['director']) if content.get('director') else None
        payload['Availability'] = content['availability'] if content.get('availability') else None
        payload['Download'] = self.check_download(content['download'])
        payload['IsOriginal'] = None
        payload['IsBranded'] = None
        payload['Subtitles'] = None
        payload['Dubbed'] = None

        if self.is_epi:
            del payload['ExternalIds']
            del payload['IsBranded']

        payload['IsAdult'] = None
        payload['Packages'] = [{'Type': 'subscription-vod'}]
        payload['Country'] = None
        payload['Timestamp'] = datetime.now().isoformat()
        payload['CreatedAt'] = self._created_at
        
        if self.is_epi:
            print(f'--- FORMATTED PAYLOAD EPISODE ', payload['Id'], ' ', payload['Title'], ' ---\n\n')
        else:
            print(f'--- FORMATTED PAYLOAD CONTENT ', payload['Id'], ' ', payload['Title'], ' ---\n\n')
            self.content.append(payload)

    def login(self):
        ''' Logins into Netflix '''

        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))).click()
            WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='id_userLoginId']"))).send_keys('julietanavarro1154@gmail.com')
            WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='id_password']"))).send_keys('darwin1154*')
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-uia='login-submit-button']"))).click()
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='profile-icon']"))).click()
            print('--- LOGIN EXITOSO ---')

        except TimeoutException:
            for _ in range(5):
                print('--- LOGIN TIMEOUT ---')


Netflix()
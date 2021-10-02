# import re
import time
import platform
import requests
from common import config
from utils.mongo import mongo
# from datetime import datetime
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By       
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
# from selenium.webdriver.firefox.options import Options as FirefoxOptions


class StarPlus():
    """
    TODO:

    - DATOS IMPORTANTES:
        - Versión Final: TODO:
        - VPN: TODO:
        - ¿Usa Selenium?: TODO:
        - ¿Usa Playwright?: TODO:
        - ¿Tiene API?: TODO:
        - ¿Usa BS4?: TODO:
        - ¿Se relaciona con scripts TP? TODO:
        - ¿Instancia otro archivo de la carpeta "platforms"?: TODO:
        - Última revisión: TODO:
        - ¿Cuanto demoró la ultima vez? TODO:
        - ¿Cuantos contenidos trajo la ultima vez? TODO:

    - OTROS COMENTARIOS:
        TODO:
    """
    def __init__(self, ott_site_uid, ott_site_country, type):
        self._config = config()['ott_sites'][ott_site_uid]
        # urls:
        self.url = 'https://www.starplus.com'
        # generic:
        self._platform_code = self._config['countries'][ott_site_country]
        self._created_at = time.strftime("%Y-%m-%d")
        self.country_code = ott_site_country
        self.name = ott_site_uid
        self.mongo = mongo()
        self.sesion = requests.session()
        # bbdd:
        self.collections = config()['mongo']['collections']
        self.database = self.collections['top_ten_hackaton']
        # data lists:
        self.prepayloads = []
        self.payloads = []
        self.payloads_epi = []
        self.scraped = []
        self.scraped_epi = []
        self.skippedTitles = 0
        self.skippedEpis = 0

        try:
            if platform.system() == 'Linux':
                Display(visible=0, size=(1366, 768)).start()
        except Exception:
            pass

        self.driver = webdriver.Firefox()
        self.content = []
        self.epis = []

        self._scraping()

        if type == 'scraping':
            self._scraping()

    def _scraping(self):
        self.login()
        self.scrap_movies()
        #self.scrap_series()

    def scrap_movies(self):
        ''' Extracts all movies data '''
        WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((
                            By.XPATH, "//a[@data-testid='navigation-item-4-PELÍCULAS']"))).click()
        time.sleep(2)
        principal = self.driver.find_element_by_css_selector(
                    "div[class='sc-hgRTRy jrzXWb']").find_elements_by_css_selector(
                    "a[class='sc-EHOje WxEV basic-card skipToContentTarget']")
        movies = []
        total = len(principal)
        counter = 0
        while True:
            if counter > 9:
                break
            try:
                WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='sc-hgRTRy jrzXWb']")))
                self.driver.find_element_by_css_selector(
                        "div[class='sc-hgRTRy jrzXWb']").find_elements_by_css_selector(
                        "a[class='sc-EHOje WxEV basic-card skipToContentTarget']")[counter].click()
                WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable(
                        (By.XPATH, "//div[@aria-selected='details']"))).click()
                content = {}
                content['id'] = self.driver.current_url.split('/')[-1]
                content['title'] = self.driver.find_element_by_css_selector(
                        "h1[class='h3 padding--bottom-6 padding--right-6 text-color--primary']").text
                content['url'] = self.driver.current_url
                content['image'] = self.driver.find_element_by_css_selector(
                        "div[class='sc-dRaagA jNrEQj']").find_element_by_tag_name('img').get_attribute('src')
                content['type'] = 'movie'
                content['synopsis'] = self.driver.find_element_by_css_selector(
                        "p[class='margin--0 body-copy body-copy--large text-color--primary']").text
                pre_data = self.driver.find_elements_by_css_selector(
                        "div[class='sc-bTiqRo eqCABb']")
                try:
                    content['duration'] = pre_data[0].find_element_by_css_selector(
                        "p[class='body-copy margin--0 text-color--primary']").text
                except IndexError:
                    content['duration'] = None
                try:
                    content['year'] = pre_data[1].find_element_by_css_selector(
                        "p[class='body-copy margin--0 text-color--primary']").text
                except IndexError:
                    content['year'] = None
                try:
                    content['genres'] = pre_data[2].find_element_by_css_selector(
                        "p[class='body-copy margin--0 text-color--primary']").text
                except IndexError:
                    content['genres'] = None
                directors_cast = self.driver.find_elements_by_css_selector(
                        "div[class='sc-blIhvV bgYJdh']")
                try:
                    names = directors_cast[0].find_elements_by_css_selector(
                        "p[class='body-copy margin--0 text-color--primary']")
                    content['directors'] = [name.text for name in names]
                except IndexError:
                    content['directors'] = None
                try:
                    names = directors_cast[1].find_elements_by_css_selector(
                        "p[class='body-copy margin--0 text-color--primary']")
                    content['cast'] = [name.text for name in names]
                except IndexError:
                    content['cast'] = None
                movies.append(content)
                print(content)

                self.driver.execute_script("window.history.go(-1)")
                time.sleep(4)
                counter += 1
            except ElementClickInterceptedException:
                self.driver.find_element_by_css_selector(
                        "button[class='sc-iiUIRa iXgoSW slick-arrow slick-next']").click()
                continue
            except IndexError:
                break

    def scrap_series(self):
        ''' Extract all series data '''

        # WebDriverWait(self.driver, 60).until(
        #                 EC.element_to_be_clickable(
        #                     (By.XPATH, "//a[@data-testid='navigation-item-5-SERIES']"))).click()
        # time.sleep(2)
        # principal = self.driver.find_elements_by_class_name(
        #             "sc-kGXeez leNgGG  asset-wrapper")
        # movies = []
        # total = len(principal)
        # counter = 0
        # while True:
        #     if counter > 9:
        #         break
        #     try:
        #         self.driver.find_elements_by_class_name(
        #                 "sc-kGXeez leNgGG  asset-wrapper")[counter].click()
        #         WebDriverWait(self.driver, 60).until(
        #                 EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@aria-selected='details']"))).click()
        #         content = {}
        #         content['id'] = self.driver.current_url.split('/')[-1]
        #         content['title'] = self.driver.find_element_by_css_selector(
        #                 "h1[class='h3 padding--bottom-6 padding--right-6 text-color--primary']").text
        #         content['url'] = self.driver.current_url
        #         content['image'] = self.driver.find_element_by_css_selector(
        #                 "div[class='sc-dRaagA jNrEQj']").find_element_by_tag_name('img').get_attribute('src')
        #         content['type'] = 'movie'
        #         content['synopsis'] = self.driver.find_element_by_css_selector(
        #                 "p[class='margin--0 body-copy body-copy--large text-color--primary']").text
        #         pre_data = self.driver.find_elements_by_css_selector(
        #                 "div[class='sc-bTiqRo eqCABb']")
        #         try:
        #             content['duration'] = pre_data[0].find_element_by_css_selector(
        #                 "p[class='body-copy margin--0 text-color--primary']").text
        #         except IndexError:
        #             content['duration'] = None
        #         try:
        #             content['year'] = pre_data[1].find_element_by_css_selector(
        #                 "p[class='body-copy margin--0 text-color--primary']").text
        #         except IndexError:
        #             content['year'] = None
        #         try:
        #             content['genres'] = pre_data[2].find_element_by_css_selector(
        #                 "p[class='body-copy margin--0 text-color--primary']").text
        #         except IndexError:
        #             content['genres'] = None
        #         directors_cast = self.driver.find_elements_by_css_selector(
        #                 "div[class='sc-blIhvV bgYJdh']")
        #         try:
        #             names = directors_cast[0].find_elements_by_css_selector(
        #                 "p[class='body-copy margin--0 text-color--primary']")
        #             content['directors'] = [name.text for name in names]
        #         except IndexError:
        #             content['directors'] = None
        #         try:
        #             names = directors_cast[1].find_elements_by_css_selector(
        #                 "p[class='body-copy margin--0 text-color--primary']")
        #             content['cast'] = [name.text for name in names]
        #         except IndexError:
        #             content['cast'] = None
        #         movies.append(content)
        #         print(content)

        #         self.driver.execute_script("window.history.go(-1)")
        #         time.sleep(4)
        #         counter += 1
        #     except ElementClickInterceptedException:
        #         self.driver.find_element_by_xpath(
        #                 "/html/body/div[1]/div/div[4]/div/main/article/div[2]/div[1]/div/div/div/div/button[2]/svg/path").click()
        #         continue
        #     except IndexError:
        #         break

    def login(self):
        ''' Logins int Starplus '''

        # self.driver.get(self.url)
        # time.sleep(5)
        # self.driver.find_element_by_xpath("//a[@href='/login']").click()
        # time.sleep(10)
        # self.driver.find_element_by_class_name('sc-gPEVay fGHsOs sc-eqIVtm csbJFj').send_keys('arturomontalvo1154@gmail.com')
        # time.sleep(2)
        # self.driver.find_element_by_xpath("//button[@data-testid='login-continue-button']").click()
        # time.sleep(3)
        # self.driver.find_element_by_xpath("//input[@id='password']").send_keys('darwin1154')
        # time.sleep(2)
        # self.driver.find_element_by_xpath("//button[@type='submit']").click()

        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))).click()
            WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='email']"))).send_keys('arturomontalvo1154@gmail.com')
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='login-continue-button']"))).click()
            WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))).send_keys('darwin1154')
            submit = self.driver.find_element_by_xpath("//button[@type='submit']")
            self.driver.execute_script("arguments[0].click();", submit)
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='sc-hmXxxW sc-clNaTc kskPda profile-avatar']"))).click()
            time.sleep(5)
            print('--- LOGIN EXITOSO ---')

        except TimeoutException:
            for _ in range(5):
                print('--- LOGIN TIMEOUT ---')

import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


class Starplus():
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
    def __init__(self):
    # bbdd:
        self.skippedTitles = 0
        self.skippedEpis = 0
        self.url = 'https://www.starplus.com'
        self.driver = webdriver.Firefox()
        self.content = []
        self.epis = []

        self._scraping()

        if type == 'scraping':
            self._scraping()

    def _scraping(self):
        self.login()
        self.scrap_movies()
        self.scrap_series()

    def scrap_movies(self):
        ''' Extracts all movies data '''
        WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='navigation-item-4-PELÍCULAS']"))).click()
        time.sleep(2)   
        principal = self.driver.find_element_by_css_selector(
                    "div[class='sc-hgRTRy jrzXWb']").find_elements_by_css_selector(
                    "a[class='sc-EHOje WxEV basic-card skipToContentTarget']")
        movies = []
        total = len(principal)
        counter = 0
        while True:
            if counter > total:
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

        WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@data-testid='navigation-item-5-SERIES']"))).click()

    def login(self):
        ''' Logins int Starplus '''

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

Starplus()
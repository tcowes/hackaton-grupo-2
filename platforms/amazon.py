from sys import set_asyncgen_hooks
import time
import requests
import hashlib
import re
import platform
import json
import pyotp
from common import config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from datetime import datetime
from handle.mongo import mongo
from updates.upload import Upload
from urllib.parse import parse_qs, urlparse
from handle.replace import _replace
from handle.datamanager import Datamanager
from handle.checkSeries import checkSeries
from selenium.webdriver.firefox.options import Options

class Amazon():
    def __init__(self, ott_site_uid, ott_site_country, operation):
        self._config            = config()['ott_sites'][ott_site_uid]
        self.country            = ott_site_country
        self._start_url         = self._config['start_url']
        self._url_api           = self._config['url_api']
        self._deeplink          = self._config['deeplink']
        self._deeplink2         = self._config['deeplink2']
        self._platform_code     = self._config['countries_data'][ott_site_country]['PlatformCode']
        self._created_at        = time.strftime('%Y-%m-%d')
        self.url_original       = self._config['url_original']
        # BBDD's.
        self.mongo                  = mongo()
        self.titanPreScraping       = config()['mongo']['collections']['prescraping']
        self.titanScraping          = config()['mongo']['collections']['scraping']
        self.titanScrapingEpisodes  = config()['mongo']['collections']['episode']
        # ACCOUNT DATA.
        self.account            = self._config['countries_data'][ott_site_country]['account']
        if self.account:
            self.loggin_info    = self._config['accounts'][self.account]
            self._user_name     = self.loggin_info['user_name']
            self._user_pass     = self.loggin_info['user_pass']
            self.cookie         = ''

        # Parámetros claves.
        self.headers        = None
        self._server_region = self._config['countries_data'][ott_site_country]['region']
        self.get_cookie     = self._config['countries_data'][ott_site_country]['cookie']

        # STORE CURRENCY
        self.get_store      = self._config['countries_data'][ott_site_country].get('get_store')
        self.currency       = self._config['countries_data'][ott_site_country].get('store_currency')
        if not self.currency:
            self.currency   = config()['currency'][ott_site_country]

        # Iniciar Session.
        self.session = requests.session()

        print(f"\nIniciando scraping\nPlatformCode: {self._platform_code}\n")

        if operation == 'scraping':

            self.browser = self.selenium_login()
            if self.browser:
                #self._preScraping(browser)
                self._scraping(testing=True)
            else:
                print("\nNo se pudo acceder a la página\nScraping Finalizado")
            self.session.close()

        def _scraping(self):
            print("hola")

        def selenium_login(self):
        """Método fundamental para iniciar el preScraping.
        Aquí nos loggeamos y accedemos a la página princial de
        Amazon Prime Video.

        Returns:
            obj: Devuelve el objeto browser (Selenium).
        """
        ##############################################################
        # Utilizamos Selenium para obtener urlsCategorias y channels #
        ##############################################################
        

        #browser = webdriver.Firefox()
        #browser.get(self._start_url)
        if self.account:
            option = Options()
            option.add_argument('--headless')
            browser = webdriver.Firefox()

            check_location = self.validate_location(browser)
            if not check_location:
                return False
            print(" ##### Ingreando vía Selenium #####")
            browser.get(self._start_url)
            print(f"Loggin a {self._start_url}")
            print(f"Usando {self.account} -> {self._user_name}")  
            username = browser.find_element_by_xpath(self._config['queries']['user_name'])
            password = browser.find_element_by_xpath(self._config['queries']['user_pass'])
            
            username.send_keys(self._user_name)
            password.send_keys(self._user_pass)
            browser.find_element_by_xpath(self._config['queries']['btn_login']).click()
            time.sleep(1)
            if self.loggin_info.get('2FA'):
                try:
                    browser.find_element_by_xpath(self._config['queries']['chk_otp']).click()
                    time.sleep(1)
                    browser.find_element_by_xpath(self._config['queries']['btn_otp']).click()
                except:
                    pass

                codes2FA = browser.find_element_by_xpath(self._config['queries']['code_2fa'])
                code2FA = self.loggin_info['2FA']
                totp = pyotp.TOTP(code2FA)
                print("Current OTP:", totp.now())
                codes2FA.send_keys(totp.now())
                browser.find_element_by_xpath(self._config['queries']['btn_login2']).click()
             
        else:
            print('No requiere login.')
            browser = webdriver.Firefox()
            check_location = self.validate_location(browser)
            if not check_location:
                return False
            browser.get('https://www.primevideo.com/')
        time.sleep(5)
        
        try:
            try:
                ok_login = browser.find_element_by_xpath("//*[@id='pv-nav-main-menu']")            
                if ok_login:
                    print("Loggin exitoso\n")
                    return browser
            except:
                timer =  browser.find_element_by_xpath("//*[@id='timer']")
                intentos = 1
                while intentos != 4:
                    print(f"\n¡¡¡Acceso Denegado!!! Intentos: ({intentos}/3)")
                    print("El usuario de la cuenta debe verificar el acceso via sms o e-mail.")
                    time_ = int(re.sub("\D", "" ,timer.text ,flags=re.IGNORECASE))
                    print(f"El usuario debe confirmar en {time_} segundos.")
                    time.sleep(time_ + 1)
                    try:
                        ok_login = browser.find_element_by_xpath("//*[@id='pv-nav-main-menu']")
                        if ok_login:
                            print("Loggin exitoso\n")
                            return browser
                    except:
                        print("El usuario no autorizó. Reenviando coonfirmación.")
                        browser.find_element_by_xpath('//*[@id="resend-approval-link"]').click()
                        time.sleep(5)
                        timer =  browser.find_element_by_xpath("//*[@id='timer']")
                        time.sleep(5)
                        intentos += 1
                browser.quit()
                return None
        except:
            print(f"\n¡¡¡Acceso Denegado!!!  ROBOT ALERT (¬¬)")
            print("Detecta que es un robot. Hacer loggin manual.")
            print("Tiempo para loggearse e ingresar: 2 min.")
            time.sleep(120)
            try:
                ok_login = browser.find_element_by_xpath("//*[@id='pv-nav-main-menu']")
                if ok_login:
                    print("Loggin exitosooooooo\n")
                    return browser
            except:
                browser.quit()
                return None    

        print("Loggin exitoso\n")
        return browser
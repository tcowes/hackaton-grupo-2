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
from utils.mongo import mongo
from urllib.parse import parse_qs, urlparse
from utils.replace import _replace
from utils.datamanager import Datamanager
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
        self.name               = ott_site_uid
        self.mongo                  = mongo()
        #self.titanPreScraping       = config()['mongo']['collections']['prescraping']
        #self.titanScraping          = config()['mongo']['collections']['scraping']
        #self.titanScrapingEpisodes  = config()['mongo']['collections']['episode']
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

        # Iniciar Session.
        self.session = requests.session()

        print(f"\nIniciando scraping\nPlatformCode: {self._platform_code}\n")

        if operation == 'scraping':            
            self.browser = self.selenium_login()
            if self.browser:
                self._scraping()
            else:
                print("\nNo se pudo acceder a la página\nScraping Finalizado")
            self.session.close()

    def _query_field(self, collection, field=None, extra_filter=None):
        find_filter = {'PlatformCode': self._platform_code, 'CreatedAt': self._created_at}

        if extra_filter:
            find_filter.update(extra_filter)

        find_projection = {'_id': 0, field: 1,} if field else None

        query = self.mongo.db[collection].find(
            filter=find_filter,
            projection=find_projection,
            no_cursor_timeout=False
        )

        if field:
            query = [item[field] for item in query]
        else:
            query = list(query)

        return query

    def Get_Cookie(self, browser):
        print("Obteniendo cookie\n")
        browser.get('https://www.primevideo.com')
        cookies = browser.get_cookies()
        head_cookies = ''
        for coo in cookies:
            if coo['name'] in ('x-wl-uid', 'session-id-time', 'session-id', 'ubid-main-av', 'session-token', 'csm-hit', 'lc-main-av', 'x-main-av', 'at-main-av', 'sess-at-main-av'):
                head_cookies += '{}={};'.format(coo['name'], coo['value'])

        self.cookie = head_cookies[:len(head_cookies)-1]

    def Get_2FA_Codes(self):
        code2FA = self._2FA_code
        totp = pyotp.TOTP(code2FA)
        print("Current OTP:", totp.now())
        return totp

    def _scraping(self):
        browser = self.browser
        self.url_base = "https://www.primevideo.com"
        soup = BeautifulSoup(browser.page_source, 'lxml')
        all_option = soup.find('ul', {'class':"pv-navigation-bar"})
        a_class = all_option.find_all("a")
        
        url_cate_serie = None
        url_cate_movie = None
        """
        for a in a_class:
            if a.string == "Películas":
                url_cate_movie =self.url_base + a["href"]            
            
            if a.string == "Series":
                url_cate_serie =self.url_base + a["href"]
        """
        print(url_cate_movie)
        print(url_cate_serie)
        
        urls_top_ten_home = self.get_url_top_ten(browser)
        print("Lista de Top 10 Home")
        print(urls_top_ten_home)
        
        if url_cate_movie:
            browser.get(url_cate_movie)
            urls_top_ten_movies = self.get_url_top_ten(browser)
            print("Lista de Top 10 Movie")
            print(urls_top_ten_movies)
        
        if url_cate_movie:
            browser.get(url_cate_movie)
            urls_top_ten_movies = self.get_url_top_ten(browser)
            print("Lista de Top 10 Series")
            print(urls_top_ten_movies)
        
        for url in urls_top_ten_home:
            self.get_payload(url, browser)
    ##################################################################       
    def get_id(self, _string):
        id = ""
        my_flag = "/"
        i = 0
        for char in _string:
            if char == my_flag:
                i += 1
            if i == 5:
                break
            if i == 4:
                id += char
        return id[1:] if id != "" else None

    def get_title(self, soup):
        title = soup.find('h1', {'class':"_2IIDsE _3I-nQy"})
        return title.string

    def get_year(self, soup):
        pass
        #_span = soup.find('span', {'class':"XqYSS8"})
        #year = _span.string
        #return year
   
    def get_type(self, soup):
        _span = soup.find_all('span', {'class':"XqYSS8"})
        if len(_span) == 1:
            return "serie"
        else:
            return "movie"
    
    def get_year_and_duration(self, soup):
        span_dur_year = soup.find_all('span', {'class':"XqYSS8"})
        print(span_dur_year)
        span_duration = span_dur_year[0].find('span')
        span_year = span_dur_year[1].find('span')

        return (span_year.string, self.get_duration(span_duration.string))

    def get_year(self, soup):
        return soup.find('span', {'class':"XqYSS8"}).string
    
    def get_synopsis(self, soup):
        span_synopsis = soup.find('span', {'class':"_3qsVvm _1wxob_"}).string
        return span_synopsis.string

    def get_img(self, soup):
        span_img = soup.find('span', {'class':"atf-full"})
        return span_img["src"]

    def get_payload(self, url, browser):
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        _type = self.get_type(soup)

        payload = {
            'PlatformName' : self.name,
            'PlatformCode' : self._platform_code,
            'Id'           : self.get_id(browser.current_url),
            'Title'        : self.get_title(soup),
            'Year'         : self.get_year_and_duration(soup)[0] if _type == "movie" else self.get_year(soup),
            'Type'         : _type,
            'Duration'     : self.get_year_and_duration(soup)[1] if _type == "movie" else None,
            'Deeplink'     : url,
            'Synopsis'     : self.get_synopsis(soup),
            'Image'        : self.get_img(soup),
            'Rating'       : None,
            'Genres'       : None,
            'Cast'         : None,
            'Directors'    : None,
            'IsOriginal'   : None,
            'TimeStap'     : datetime.now().isoformat(),
            'Episodes'     : None,
            'ParentId'     : None,
            'ParentTitle'  : None,
            'Episode'      : None,
            'Season'       : None,
            'Seasons'      : None,
            'Number'       : None,
            'Crew'         : None,
        }
        print(payload)
        return payload

    def get_url_top_ten(self, browser):
        elem = browser.find_element_by_tag_name(self._config['queries']['html'])
        time.sleep(1)
        elem.send_keys(Keys.END)
        elem.send_keys(Keys.END)
        elem.send_keys(Keys.END)
        elem.send_keys(Keys.END)
        buttons = browser.find_elements_by_xpath("//button[@class='_3Twtd7 _2MTjs9']")
        time.sleep(4)
        buttons[5].click()
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        divs = soup.find_all('div', {'class':"ezyzj6"})
        urls = []
        for div in divs:
            a_tag = div.find("a")
            urls.append(self.url_base+a_tag.get("href"))
        print("Del top 10 conseguí: "+str(len(urls)))
        return urls
        
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
    
    def validate_location(self, browser):
        print('\n****** Validando ubicación *****')
        if self.country != 'LATAM':
            browser.get('https://www.primevideo.com')
            #############################
            #       LOCATION VPN        #
            #############################
            html = browser.page_source
            soup = BeautifulSoup(html,'html.parser')
            script = soup.find('script', attrs={'type':'text/template'}).text
            script_json = json.loads(script)
            try:
                location = script_json['initArgs']['context']
            except KeyError:
                location = script_json['props']['context']
            currentTerritory = location['currentTerritory']
            recordTerritory = location['recordTerritory']
            if currentTerritory != self.country:
                print('****************************************************************************************')
                print('**            No se ha conectado al pais correcto, el pais detectado es: ' + currentTerritory + '           **')
                print('**                         Verificar VPN. Se detiene scraping.                        **')
                print('****************************************************************************************')
                browser.close()
                time.sleep(5)
                browser.quit()
                time.sleep(5)
                return False
            else:
                print('Estas conectado correctamente a: ' + self.country + '\nSe inicia scraping.\n')
        else:
                print('Estas conectado correctamente a: ' + 'LATAM' + '\nSe inicia scraping.\n')
        return browser
    
    def get_duration(self, duration_text):
        """
        Método para obtener duracion de contenido

        Args:
            duration_text [str]: duracion en formato NUMh NUMmin 

        Retruns:
            duration [int]: duracion en minutos
        """
        try: 
            if 'h' in duration_text:
                horas, minutos = duration_text.split('h')
            else:
                horas = None
                minutos = duration_text

            horas = int(re.findall(r'\d+', horas)[0]) if horas else 0
            minutos = int(re.findall(r'\d+', minutos)[0]) if minutos and minutos.strip() != '' else 0

            duration = horas * 60 + minutos 
            duration = duration if duration != 0 else None
        except Exception:
            return None
        
        return duration
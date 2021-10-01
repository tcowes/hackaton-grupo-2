import pymongo 
from mongo.connection import MongoDB
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions

class Netflix():
    def __init__(self):
        self.db = MongoDB()
        self.url = 'https://www.netflix.com/'
        self.driver = webdriver.Firefox()
        self.scraping()
    
    def scraping(self):
        self.login()
    
    def login(self):
        ''' Logins into Netflix '''

        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))).click()
            WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@href-label='/login']"))).click()
            

        except selenium.common.exceptions.TimeoutException:
            for _ in range(5):
                print('--- LOGIN TIMEOUT ---')

if __name__ =='__main__':
    Netflix()

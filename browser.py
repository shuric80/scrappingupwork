import sys
import time
from datetime import datetime
import logging
from importlib import import_module
import importlib.util
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import requests
from bs4 import BeautifulSoup

from header import header

logger = logging.getLogger(__file__)

URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
TIMEOUT = 10

class Browser:
    @staticmethod
    def create(name_browser):
        lib_path = 'selenium.webdriver.{}.webdriver'.format(name_browser)
        if importlib.util.find_spec(lib_path) is None:
            logger.error('No found module browser')
            raise Exception()

        browser = import_module(lib_path)
        return browser


class Options:
    @staticmethod
    def create(name_options):
        lib_path = 'selenium.webdriver.{}.options'.format(name_options)
        if importlib.util.find_spec(lib_path) is None:
            logger.error('No found module options')
            raise Exception()

        options = import_module(lib_path)
        return options



class AuthenticationPageUpwork:
    def __init__(self, browser):
        self.browser = browser   

    def getLoginForm(self):
        self.browser.get(URL_LOGIN)

    def fillLoginForm(self, login):
        self.wait_download('login_username').send_keys(login)
        #self.browser.find_element_by_id('login_username').send_keys(login)
        self.browser.find_element_by_css_selector('.btn-block-sm.width-sm.btn.btn-primary.m-0.text-capitalize').click()
        #self.browser.find_element_by_xpath("//button[@type='submit']").submit()

    def wait_download(self, elem):

        try:
            elem = WebDriverWait(self.browser, TIMEOUT).until(
              EC.visibility_of_element_located((By.ID, elem)))        
        except TimeoutException:
            logger.error('Timeout interput.')
        else:
            logger.debug('Page download: Done. URL:{}'.format(self.browser.current_url))

        return elem


    def fillPasswordForm(self, password):
        self.wait_download('login_password').send_keys(password)
        #self.browser.find_element_by_id('login_password').send_keys(password)
        self.browser.find_element_by_css_selector('.checkbox-replacement-helper').click()
        self.browser.find_elements_by_css_selector('.btn-block-sm.width-sm.btn.btn-primary.m-0.text-capitalize')[1].click()


class BrowserContext:
    def __init__(self, name='firefox', headless=False):
        options = Options.create(name).Options()
        options.headless = headless
        self.browser = Browser.create(name).WebDriver(options=options)        
        #self.browser.implicitly_wait(30)
 

    def __enter__(self):
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):       
        if exc_type:
            self.browser.save_screenshot('screenshot.png')
            logger.error('{}{}{}'.format(exc_type, exc_val, exc_tb))
        
        self.browser.close()       
        logger.info('Browser closed')


class Authentication:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.cookies = None     


    def do(self, browser = 'firefox', headless=False):        
        with BrowserContext(browser, headless) as w:
            f = AuthenticationPageUpwork(w)
            f.getLoginForm()
            f.fillLoginForm(self.login)
            f.fillPasswordForm(self.password)
            self.cookies = w.get_cookies()


    def saveCookies(self):
        with open('cookies.pl', 'wb') as f:
            pickle.dump(self.cookies, f)

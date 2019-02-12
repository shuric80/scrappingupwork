import sys
import os
import time
import random
from datetime import datetime
import logging
from importlib import import_module
import importlib.util
import pickle
#from collections import namedtuple
from dataclasses import dataclass
#from celery import Celery
import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import db

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
#logging.basicConfig(filename='logs/log.txt', level=logging.DEBUG)
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

#app = Celery('tasks', backend='amqp', broker='amqp://')
URL_MAIN = 'https://www.upwork.com'
URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
URL_FIND = 'https://www.upwork.com/ab/find-work'
TIMEOUT = 5

POST_FIELDS_PATTERN = dict(
    title='.//h4[@data-job-title]',
    url='.//a[@data-ng-href]',
    ptype='.//span[@data-job-type]',
    duration='.//span[@data-job-duration]',
    posted_time='.//time',
    tags='.//span[@data-job-sands-attrs]',
    description='.//div[@data-job-description]',
    proposal='.//span[@data-job-proposals]',
    verified='.//span[@data-job-client-payment-verified]',
    spent='.//span[@data-job-client-spent-tier]',
    location='.//span[@data-job-client-location]',
    feedback='.//span[@data-eo-rating]')
#.get_attribute('data-eo-popover-html-unsafe')


class Post:
    """storage job post
      """
    @classmethod
    def parse(cls, section):
        for name, pattern in POST_FIELDS_PATTERN.items():
            try:
                elem = section.find_element_by_xpath(pattern)
            except NoSuchElementException as e:
                elem = None
                logger.error('No such element:{}'.format(name))
            finally:
                setattr(cls, name, elem)

        return cls

    def __repr__(self):
        return getattr(self, 'title')



class Browser:
    @staticmethod
    def create(name_browser):
        lib_path = 'selenium.webdriver.{}.webdriver'.format(name_browser)
        if importlib.util.find_spec(lib_path) is None:
            logger.error('No found module browser')
            raise Exception()

        browser = import_module(lib_path)
        options = browser.Options()
        logger.debug('Browser: {}'.format(name_browser))
        return browser, options


class Driver:
    @staticmethod
    def create(name_browser, headless):
        browser, options = Browser.create(name_browser)
        options.headless = headless
        #options.add_argument("user-data-dir=/home/shuric/.config/chromium/")
        driver = browser.WebDriver(options=options)
        driver.maximize_window()
        driver.wait = WebDriverWait(driver, 30)
        return driver


class DriverConn:
    def __init__(self, name, headless=True):
        self.name = name
        self.headless = headless
        self.driver = None

    def __enter__(self):
        self.driver = Driver.create(self.name, self.headless)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.driver.save_screenshot('logs/screenshot_{}.png'.format(datetime.now()))
            self.driver.close()
            raise Exception('{}:{}'.format(exc_type, exc_val))


class Cookies:
    @staticmethod
    def add(cookies):
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)

    @staticmethod
    def is_exist():
        return os.path.isfile('cookies.pkl')

    @staticmethod
    def getAll():
        with open('cookies.pkl', 'rb') as f:
            return pickle.load(f)


class User:
    @staticmethod
    def get():
        with open('user.txt', 'r') as f:
            login, password = f.read().split(':')

        return login, password


class UpworkProcess:
    def __init__(self):
        self.driver = None


    def fillLoginPage(self, login):
        elem = self.driver.wait.until(EC.presence_of_element_located((By.ID, 'login_username')))
        UpworkProcess.fillForm(elem, login)
        self.driver.find_element_by_xpath("//button[@type='submit' and text()='Continue']").click()
        logger.debug('Login submit.')

    def fillPasswordPage(self, password):
        elem = self.driver.wait.until(EC.presence_of_element_located((By.ID, 'login_password')))
        UpworkProcess.fillForm(elem, password)
        self.driver.find_element_by_class_name('checkbox').click()
        time.sleep(random.gauss(0.8, 0.2))
        self.driver.find_element_by_xpath("//button[@type='submit' and text()='Log In']").click()
        #assert  "Oops! Password is incorrect." not in self.driver.page_source
        logger.debug('Password submit.')

    def setCookies(self):
        self.driver.get(URL_MAIN)
        self.driver.delete_all_cookies()
        for cookie in Cookies.getAll():
            self.driver.add_cookie(cookie)

        self.driver.refresh()
        logger.debug('Cookies append in browser.')

    def authentication(self):
        login, password = User.get()
        self.driver.get(URL_LOGIN)
        self.fillLoginPage(login)
        time.sleep(TIMEOUT)
        self.fillPasswordPage(password)

        logger.info('Authentication upwork profile: Verified')


    def selectJobsPerPage(self):
        search_box = self.driver.wait.until(EC.presence_of_element_located((By.ID, 'search-box-el')))
        search_box.submit()
        select = self.driver.wait.until(EC.presence_of_element_located((By.TAG_NAME,'data-eo-select')))
        select.click()
        select.find_elements_by_tag_name('li')[2].click()


    @staticmethod
    def fillForm(elem, text, ex=0.8):
        for w in text:
            timeout = random.gauss(ex, ex*0.4)
            if not timeout > 0:
                timeout = ex

            time.sleep(round(timeout, 2))
            elem.send_keys(w)

    def getJobFeed(self, text):
        search_box = self.driver.wait.until(EC.presence_of_element_located((By.ID, 'search-box-el')))
        search_box.clear()
        time.sleep(1)
        UpworkProcess.fillForm(search_box, text)
        search_box.submit()

    def parseJobFeed(self, word):
        time.sleep(TIMEOUT)
        #self.driver.wait.until(EC.title_is('Freelance Python Jobs Online - Upwork'))
        #self.driver.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'section')))
        #self.driver.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'section')))
        sections = self.driver.find_elements_by_tag_name('section')
        return sections


    def run(self, headless=True):
        with DriverConn('firefox', headless) as self.driver:
            if Cookies.is_exist():
                self.setCookies()
                #logger.debug('Cookies appended in browser.')
            else:
                self.authentication()
                time.sleep(TIMEOUT)
                cookies = self.driver.get_cookies()
                Cookies.add(cookies)
                logger.debug('Cookies saved.')

            self.selectJobsPerPage()
            logger.debug('Choosed 50 posts on page.')
            self.scrapy()

    def scrapy(self):
        for word in db.getWordsSearch():
            logger.info('Loading page: Key word: {}'.format(word))
            self.getJobFeed(word)
            sections = self.parseJobFeed(word)
            posts = list()
            for section in sections:
                posts.append(Post(section))

            db.addPosts(posts, word)
            logger.debug('Count found posts: {}'.format(len(posts)))

@app.task
def start():
    up = UpworkProcess()
    up.run(headless=True)



if __name__ == '__main__':

    headless = True if '--headless' in sys.argv[1:] else False

    if sys.argv[1] == 'create':
        db.createDB()

    elif sys.argv[1] == '--append':
        for w in sys.argv[2:]:
            logger.debug('add search word:{}'.format(w))
            db.addWordsSearch(w)

    elif sys.argv[1] == 'start':
        start()

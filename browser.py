import sys
import os
import time
import random
from random import shuffle
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
    title='.//header',
    #url='.//a[@data-ng-href]',
    #ptype=".//strong[text()='Project Type:']/parent::li/span",
    ptype=".//i[contains(@class,'jobdetails-tier-level-icon')]/parent::li/small",
    posted_time=".//span[@itemProp='datePosted']",
    duration=".//ul[@class='job-features p-0']/li",
    #tags='.//span[@data-job-sands-attrs]',
    description=".//div[@class='job-description']",
    proposal=".//h4[text()='Activity on this job']/parent::section/ul/li",
    #verified='.//span[@data-job-client-payment-verified]',
    #spent='.//span[@data-job-client-spent-tier]',
    location='.//span[@data-job-client-location]',
    feedback=".//span[@itemprop='ratingValue']"
    )
#.get_attribute('data-eo-popover-html-unsafe')


class Post:
    """storage job post
      """
    @classmethod
    def parse(cls, section, url):
        """ create post storage
         """
        post = cls()
        post.url = url
        for name, pattern in POST_FIELDS_PATTERN.items():
            try:
                elem = section.find_element_by_xpath(pattern)
            except NoSuchElementException as e:
                elem = None
                logger.error('No such element:{}'.format(name))
            else:
                if name == 'url':
                    setattr(post, name, elem.get_attribute('text'))
                elif name == 'posted_time':
                    setattr(post, name, elem.get_attribute('datetime'))
                elif name == 'feedback':
                    setattr(post, name, elem.get_attribute('data-eo-popover-html-unsafe'))
                elif hasattr(elem, 'text'):
                    setattr(post, name, elem.text)
                else:
                    pass
        return post


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
        driver.wait = WebDriverWait(driver, 60)
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
            #self.driver.close()
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


class UpworkPage:
    def __init__(self):
        self._driver =None

    def getUrls(self):
        urls = [url.get_attribute('href') for url in self._driver.find_elements_by_xpath(".//h4[contains(@class,'job-title')]/a")]
        return urls

    def setDriver(self, driver):
        self._driver = driver

    def fillForm(self, elem, text, ex=0.8):
        for w in text:
            timeout = random.gauss(ex, ex*0.4)
            if not timeout > 0:
                timeout = ex

            time.sleep(round(timeout, 2))
            elem.send_keys(w)

    def setLogin(self, login):
        elem = self._driver.wait.until(EC.presence_of_element_located((By.ID, 'login_username')))
        self.fillForm(elem, login)
        self._driver.find_element_by_xpath("//button[@type='submit' and text()='Continue']").click()
        logger.debug('Login submit.')

    def setPassword(self, password):
        elem = self._driver.wait.until(EC.presence_of_element_located((By.ID, 'login_password')))
        self.fillForm(elem, password)
        self._driver.find_element_by_class_name('checkbox').click()
        ## Human
        time.sleep(random.gauss(0.8, 0.2))
        self._driver.find_element_by_xpath("//button[@type='submit' and text()='Log In']").click()
        logger.debug('Password submit.')

    def selectJobsPerPage(self):
        search_box = self._driver.wait.until(EC.presence_of_element_located((By.ID, 'search-box-el')))
        search_box.submit()
        select = self._driver.wait.until(EC.presence_of_element_located((By.TAG_NAME,'data-eo-select')))
        select.click()
        select.find_elements_by_tag_name('li')[2].click()

    def getJobFeed(self, text):
        #elem = self._driver.find_element_by_xpath(".//button[@class='btn p-xs-left-right dropdown-toggle']").click()
        #elem = self._driver.find_elements_by_tag_name(".//input[@data-qa='ee-input']")
        #elem.clear()
        #search_box = self._driver.wait.until(EC.presence_of_element_located((By.ID, 'search-box-el')))
        #search_box.clear()
        elem = self._driver.find_element_by_id('search-box-el')
        time.sleep(1)
        self.fillForm(elem, text)
        time.sleep(1)
        #elem.submit()
        self._driver.find_element_by_xpath(".//button[@class='btn btn-primary']").click()

    def parseJobFeed(self, word):
        time.sleep(TIMEOUT)
        #self.driver.wait.until(EC.title_is('Freelance Python Jobs Online - Upwork'))
        #self.driver.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'section')))
        #self.driver.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'section')))
        sections = self._driver.find_elements_by_tag_name('section')
        return sections


class UpworkProcess:
    def __init__(self):
        self._driver = None
        self._page = UpworkPage()

    def goMainPage(self):
        self._driver.get('https://www.upwork.com/o/jobs/browse/')

    def setCookies(self):
        self._driver.get(URL_MAIN)
        self._driver.delete_all_cookies()
        for cookie in Cookies.getAll():
            self._driver.add_cookie(cookie)

        self._driver.refresh()
        logger.debug('Cookies append in browser.')

    def authentication(self):
        login, password = User.get()
        self._driver.get(URL_LOGIN)

        self._page.setLogin(login)
        #time.sleep(TIMEOUT)
        self._page.setPassword(password)
        logger.info('Authentication upwork profile: Verified')

    @property
    def cookies(self):
        return self._driver.get_cookies()

    @classmethod
    def run(cls, headless=True):
        up = cls()
        with DriverConn('firefox', headless) as up._driver:
            up._page.setDriver(up._driver)

            #if Cookies.is_exist():
            #    up.setCookies()
            #else:
            #    up.authentication()
            #    time.sleep(TIMEOUT)
            #    Cookies.add(up.cookies)
            #    logger.debug('Cookies saved.')
            up.goMainPage()
            up.downloadPages()

    def gotoUrl(self, url):
        self._driver.get(url)

    def downloadPages(self):
        #time.sleep(1)
        #self._page.selectJobsPerPage()
        for word in db.getWordsSearch():
            logger.info('Download page: Key word: {}'.format(word['text']))
            self._page.getJobFeed(word['text'])
            time.sleep(1)
            sections = self._page.parseJobFeed(word)
            posts = list()
            time.sleep(2)
            for url in self._page.getUrls():
                time.sleep(5)
                logger.debug('Goto: {}'.format(url))
                self.gotoUrl(url)
                #WebDriverWait(self._driver, 120).until(
                #EC.text_to_be_present_in_element(
                #  By.TAG_NAME, "h1"), "Job details")
                item = self._driver.find_element_by_tag_name('body')
                post = Post.parse(item, url)
                logger.debug(post.title)
                posts.append(post)

            db.addPosts(posts, word['text'])
            logger.debug('Count found posts: {}'.format(len(posts)))


if __name__ == '__main__':
        UpworkProcess.run(headless=False)

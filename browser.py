import sys
import time
from datetime import datetime
import logging
from importlib import import_module
import importlib.util
import pickle
#from collections import namedtuple
from dataclasses import dataclass
#from celery import Celery
import getpass

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import db

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

#app = Celery('tasks', backend='amqp', broker='amqp://')

URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
URL_FIND = 'https://www.upwork.com/ab/find-work'
TIMEOUT = 10


class Post:
    pass



class Browser:
    @staticmethod
    def create(name_browser):
        lib_path = 'selenium.webdriver.{}.webdriver'.format(name_browser)
        if importlib.util.find_spec(lib_path) is None:
            logger.error('No found module browser')
            raise Exception()

        browser = import_module(lib_path)
        logger.debug('Browser: {}'.format(name_browser))
        return browser


class Options:
    @staticmethod
    def create(name_options):
        lib_path = 'selenium.webdriver.{}.options'.format(name_options)
        if importlib.util.find_spec(lib_path) is None:
            logger.error('No found module options')
            raise Exception()

        options = import_module(lib_path)
        logging.debug('Options: {}'.format(name_options))
        return options


class Driver:
    @staticmethod
    def create(name_browser, headless):
        options = Options.create(name_browser).Options()
        options.headless = headless
        #options.add_argument('-private')
        #options.add_argument("user-data-dir=/tmp/browser")
        browser = Browser.create(name_browser).WebDriver(options=options)
        #if session_id:
        #    browser.session_id = session_id
        browser.wait = WebDriverWait(browser, 5)
        return browser


class DriverConn:
    name: str
    headless: bool
    def __init__(self, name, headless=True):
        self.name = name
        self.headless = headless

    def __enter__(self):
        self.driver = Driver.create(self.name, self.headless)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.driver.save_screenshot('screenshot_{}.png'.format(datetime.now()))
            self.driver.close()
            raise Exception('{}:{}'.format(exc_type, exc_val))


class Cookies:

    @staticmethod
    def add(cookies):
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)

    @staticmethod
    def get():
        with open('cookies.pkl', 'rb') as f:
            return pickle.load(f)


class UpworkProcess:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def authentication(self, headless=True):
        with DriverConn('firefox', headless) as driver:
            driver.get(URL_LOGIN)
            #assert "Log in and get to work." in driver.page_source
            driver.wait.until(EC.presence_of_element_located((By.ID, 'login_username'))).send_keys(self.login)
            driver.find_element_by_xpath("//button[@type='submit' and text()='Continue']").click()
            time.sleep(2)

            driver.wait.until(EC.presence_of_element_located((By.ID, 'login_password'))).send_keys(self.password)
            time.sleep(2)
            #driver.find_elements_by_class_name('checkbox').click()
            time.sleep(1)
            driver.find_element_by_xpath("//button[@type='submit' and text()='Log In']").click()
            #time.sleep(2)
            #assert  "Oops! Password is incorrect." not in driver.page_source

            Cookies.add(driver.get_cookies())

            driver.get(URL_FIND)

            for word in db.getWordsSearch():
                time.sleep(TIMEOUT)
                html_posts = UpworkProcess.findJobs(driver, word)
                posts = list()

                for html_post in html_posts:
                    posts.append(UpworkProcess.parseHTMLPost(html_post))

                db.addPosts(posts, word)



    @staticmethod
    def findJobs(driver, text):
        search_box = driver.wait.until(EC.presence_of_element_located((By.ID, 'search-box-el')))
        search_box.clear()
        search_box.send_keys(text)
        search_box.submit()
        time.sleep(1)
        driver.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'section')))
        sections = driver.find_elements_by_tag_name('section')

        return sections


    @staticmethod
    def parseHTMLPost(html):
        post = Post()
        post.title = html.find_element_by_xpath('.//h4[@data-job-title]').text
        post.url = html.find_element_by_xpath('.//a[@data-ng-href]').get_attribute('href')
        post.ptype = html.find_element_by_xpath('.//span[@data-job-type]').text
        post.tier = html.find_element_by_xpath('.//span[@data-job-tier]').text
        post.duration = html.find_element_by_xpath('.//span[@data-job-duration]').text
        post.posted_time = html.find_element_by_xpath('.//time').get_attribute('datetime')
        post.tags = html.find_element_by_xpath('.//span[@data-job-sands-attrs]').text
        post.description = html.find_element_by_xpath('.//div[@data-job-description]').text
        post.proposal = html.find_element_by_xpath('.//span[@data-job-proposals]').text
        post.payment = html.find_element_by_xpath('.//span[@data-job-client-payment-verified]').text
        post.spent = html.find_element_by_xpath('.//span[@data-job-client-spent-tier]').text
        post.location = html.find_element_by_xpath('.//span[@data-job-client-location]').text
        return post


    @staticmethod
    def loop(headless=True):
        with DriverConn('firefox', headless) as driver:
            driver.get('https://www.upwork.com/')

            for cookie in Cookies.get():
                logger.debug('add cookie:{}'.format(cookie))
                driver.add_cookie(cookie)

            time.sleep(5)
            driver.get(URL_FIND)

            for word in db.getWordsSearch():
                time.sleep(TIMEOUT)
                html_posts = UpworkProcess.findJobs(driver, word)
                posts = list()
                time.sleep(2)

                for html_post in html_posts:
                    posts.append(UpworkProcess.parseHTMLPost(html_post))

                db.addPosts(posts, word)


    # def setJobsPerPage(self):
    #     """[10, 20, 50]
    #     """
    #     elem = self.browser.find_element_by_tag_name('data-eo-select')
    #     if elem.text != '50':
    #        elem.click()
    #        selects = elem.find_elements_by_class_name('ng-binding')
    #        selects[3].click()
    #        time.sleep(5)


if __name__ == '__main__':
    if sys.argv[1] == 'create':
        db.createDB()

    elif sys.argv[1] == '-a':
        for w in sys.argv[2:]:
            logger.debug('add search word:{}'.format(w))
            db.addWordsSearch(w)

    elif sys.argv[1] == 'auth':
        login = input('login: ')
        password = getpass.getpass('password: ')
        a = UpworkProcess(login, password)
        a.authentication(headless=False)

    elif sys.argv[1] == 'start':
        UpworkProcess.loop(headless=False)

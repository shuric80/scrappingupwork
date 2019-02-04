import sys
import time
import csv
import logging
from importlib import import_module
import importlib.util

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import getpass

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
URL_FIND = 'https://www.upwork.com/ab/find-work'
TIMEOUT = 10


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
    def create(name_browser, headless, session_id):
        options = Options.create(name_browser).Options()
        options.headless = headless
        browser = Browser.create(name_browser).WebDriver(options=options)
        if session_id:
            browser.session_id = session_id
        browser.wait = WebDriverWait(browser, 5)
        return browser

class DriverConn:
    def __init__(self, name, headless=True, session_id=None):
        self.name = name
        self.headless = headless
        self.session_id = session_id

    def __enter__(self):
        self.driver = Driver.create(self.name, self.headless, self.session_id)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        if exc_val:
            #self.driver.save_screenshot('screenshot.png')
            raise


class UpworkProcess:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.session_id = None

    def authentication(self):
        with DriverConn('firefox') as driver:
            driver.get(URL_LOGIN)
            driver.wait.until(EC.presence_of_element_located((By.ID, 'login_username'))).send_keys(self.login)
            driver.find_element_by_xpath("//button[@type='submit' and text()='Continue']").click()

            driver.wait.until(EC.presence_of_element_located((By.ID, 'login_password'))).send_keys(self.password)
            driver.find_elements_by_class_name('checkbox').click()
            driver.find_element_by_xpath("//button[@type='submit' and text()='Log In']").click()

            self.session_id = driver.session_id


    def find(self):
        with DriverConn('firefox',  self.session_id) as driver:
            driver.get(URL_FIND)



class UpworkJobFeed:
    def __init__(self, browser):
        self.browser = browser

    @staticmethod
    def parse(sections):
        posts = list()
        for section in sections:
           title = section.find_element_by_tag_name('h4').text
           properties = section.find_element_by_tag_name('small').text
           description = section.find_element_by_xpath('//div[@data-job-description]').text
           posts.append(dict(title = title, properties = properties, description=description))

        return posts


    def search(self, text):
        elem = self.browser.find_element_by_id('search-box-el')
        elem.clear()
        elem.send_keys(text)
        elem.submit()

    def grapJobFeed(self):
        return self.browser.find_elements_by_tag_name('section')

    def setJobsPerPage(self):
        """[10, 20, 50]
        """
        elem = self.browser.find_element_by_tag_name('data-eo-select')
        if elem.text != '50':
           elem.click()
           selects = elem.find_elements_by_class_name('ng-binding')
           selects[3].click()
           time.sleep(5)


if __name__ == '__main__':

    login = input('Login [%s]:' % getpass.getuser())
    password = getpass.getpass('Password:')
    a = UpworkAuthentication(login, password)
    a.do(headless=True)
    sys.exit(0)
    page = UpworkJobFeed(a.browser)
    #time.sleep(5)
    #page.search('')
    #time.sleep(5)
    #page.setJobsPerPage()
    while True:
        q = input('Search: ')
        page.search(q)
        time.sleep(5)
        sections = page.grapJobFeed()
        posts = UpworkJobFeed.parse(sections)

        with open('results.csv', 'a', newline='') as f:
            fieldnames = ['title', 'properties', 'description']
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            writer.writerows(posts)

        sys.stdout.write('Done. Find jobs: {}\n'.format(len(posts)))

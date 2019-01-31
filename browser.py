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

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


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


class AuthenticationPageUpwork:
    def __init__(self, browser):
        self.browser = browser   

    def getLoginForm(self):
        self.browser.get(URL_LOGIN)

    def fillLoginForm(self, login):
        self.wait_download('login_username').send_keys(login)
        self.browser.find_element_by_css_selector('.btn-block-sm.width-sm.btn.btn-primary.m-0.text-capitalize').click()
        logger.debug('Send login:{}'.format(login))


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
        self.browser.find_element_by_css_selector('.checkbox-replacement-helper').click()
        self.browser.find_elements_by_css_selector('.btn-block-sm.width-sm.btn.btn-primary.m-0.text-capitalize')[1].click()
        logger.debug('Password send.')       



class UpworkAuthentication:
    def __init__(self, login, password):
        self.login = login
        self.password = password      
        self.browser = None

    def do(self, browser = 'firefox', headless=False):
        options = Options.create(browser).Options()        
        self.browser = Browser.create(browser).WebDriver(options=options)          
        try:
           f = AuthenticationPageUpwork(self.browser)
           f.getLoginForm()
           f.fillLoginForm(self.login)
           f.fillPasswordForm(self.password)
        except e:
           logger.error('Authentication fail: {}\n Create screenshot'.format(e))
           self.browser.save_screenshot('screenshot.png')  
           self.browser.close()
        else:
           logging.info('Authentication done. Browser running.')
        

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
    a.do()
    page = UpworkJobFeed(a.browser)
    time.sleep(5)    
    page.search('')
    time.sleep(5)
    page.setJobsPerPage()
    while True:
        q = input('Search: ')
        page.search(q)
        time.sleep(5)  
        sections = page.grapJobFeed()        
        posts = UpworkJobFeed.parse(sections)      

        with open('results.csv', 'w', newline='') as f:
            fieldnames = ['title', 'properties', 'description']
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            writer.writerows(posts)

        sys.stdout.write('Done. Find jobs: {}\n'.format(len(posts)))
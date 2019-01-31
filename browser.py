import sys
import time
import logging
from importlib import import_module
import importlib.util

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


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


class JobFeed:
    @staticmethod
    def parse(section):
        title = section.find_element_by_tag_name('h4').text
        properties = section.find_element_by_tag_name('small').text
        return dict(title = title, properties = properties)


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


    def search(self, name):
        elem = self.browser.find_element_by_id('search-box-el')
        elem.clear()
        elem.send_keys(name)
        elem.submit()

    def grapJobFeed(self):
        return self.browser.find_elements_by_tag_name('section')


    def setJobsPerPage(self):
        """[10, 20, 50]
        """ 
        elem = self.browser.find_element_by_tag_name('data-eo-select')
        elem.click()
        selects = elem.find_elements_by_class_name('ng-binding')
        selects[3].click()         



class BrowserContext:
    def __init__(self, name='firefox', headless=False):
        options = Options.create(name).Options()
        options.headless = headless
        self.browser = Browser.create(name).WebDriver(options=options)       


    def __enter__(self):
        return self.browser


    def __exit__(self, exc_type, exc_val, exc_tb):       
        if exc_type:
            self.browser.save_screenshot('screenshot.png')
            logger.error('{}{}{}'.format(exc_type, exc_val, exc_tb))
        
        self.browser.close()       
        logger.info('Browser close.')


class Authentication:
    def __init__(self, login, password):
        self.login = login
        self.password = password  

    def do(self, browser = 'firefox', headless=False):        
        with BrowserContext(browser, headless) as w:
            f = AuthenticationPageUpwork(w)
            f.getLoginForm()
            f.fillLoginForm(self.login)
            f.fillPasswordForm(self.password)     
            time.sleep(5)
            f.search('python')
            time.sleep(5)
            f.setJobsPerPage()
            time.sleep(10)
            for job in f.grapJobFeed():
                jobs = JobFeed.parse(job)


if __name__ == '__main__':
    a = Authentication('shuric80@gmail.com', 'Volgograd3')
    a.do( headless = False)

    sys.stdout.write('Done. Jobs: {}'.format(len(a.jobs)))
import requests
from bs4 import BeautifulSoup

URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
HEADER = { 'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'}

class LoginFormUpwork:
    def __init__(self, login=None, password=None):
        self._login = login
        self._password = password
        self.client = requests.Session()


    def getLoginForm(self):
        form = self.client.get(URL_LOGIN, headers=HEADER)
        assert form.status_code == 200
        return form

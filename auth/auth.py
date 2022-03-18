import os
import json
import time
from selenium import webdriver

class Auth:
    URL = 'http://localhost:8080'

    def login():
        driver = webdriver.Chrome()
        driver.get(Auth.URL)

    def checkJWT(token):
        '''check if jwt is still valid'''

    def __init__(self):
        '''
        self.jwt, self.refresh = Auth.login()
        
        checkJWT(jwt)

        etc.

        '''

if __name__ == "__main__":
    auth = Auth()
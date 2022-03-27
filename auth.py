import os
import json
import time
import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

class Auth:
    AUTH_URL = 'https://test-74c4e.web.app/'

    def setEnvVars(jwt, refresh):
        os.environ['EXAM_GUARD_TOKEN'] = jwt
        os.environ['EXAM_GUARD_REFRESH'] = refresh

    def getEnvVars():
        return (os.environ['EXAM_GUARD_TOKEN'], os.environ['EXAM_GUARD_REFRESH'])

    def login():
        driver = uc.Chrome()
        driver.get(Auth.AUTH_URL)

        try:
            WebDriverWait(driver, 180).until(expected_conditions.url_contains('#success'))
            jwt = driver.execute_script('return window.localStorage.getItem("jwt")')
            refresh = driver.execute_script('return window.localStorage.getItem("refresh")')
            Auth.setEnvVars(jwt, refresh)
            return (jwt, refresh)
        except TimeoutException as e:
            print(e)
            driver.close()
            exit()

    def checkJWT(decrptedJWT):
        '''check if jwt is still valid'''

    def decryptJWT(jwt):
        '''decrypt jwt and checkJWT()'''

    def refreshJWT(refreshToken):
        '''get new jwt from refresh token'''

    def __init__(self):
        try:
            self.jwt, self.refresh = Auth.getEnvVars()
        except KeyError:
            self.jwt, self.refresh = Auth.login()
        
        '''jwtDict = decrptedJWT(jwt)

        self.uid = jwtDict['user-id']
        self.name = jwtDict['name']
        ...
        etc.
        '''

if __name__ == "__main__":
    auth = Auth()
    print(auth.jwt)
    print(auth.refresh)
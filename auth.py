import os
import json
import time
import requests
import math
from google.auth import jwt as jt
import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

class Auth:
    AUTH_URL = 'https://exam-guard-desktop-auth.web.app/'
    AUTH_API_KEY = 'AIzaSyDk2zZgj6v3lYXP7t2nMRt_ed0Yx_GHUDs'

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
        except Exception as e:
            print(e)
            driver.close()
            exit()

    def decryptJWT(jwt):
        keys = requests.get('https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com')
        keys.raise_for_status()

        publicKey = list(keys.json().values())[0]

        return jt.decode(jwt, publicKey, verify=False)

    def refreshJWT(refreshToken):
        return requests.post('https://securetoken.googleapis.com/v1/token?key=' + Auth.AUTH_API_KEY, data={'grant_type': 'refresh_token', 'refresh_token': refreshToken}).json()['id_token']

    def __init__(self):
        try:
            self.jwt, self.refresh = Auth.getEnvVars()
        except KeyError:
            self.jwt, self.refresh = Auth.login()

    def getToken(self):
        return Auth.decryptJWT(self.jwt)
    
    def refreshToken(self):
        self.jwt = Auth.refreshJWT(self.refresh)

if __name__ == "__main__":
    auth = Auth()
    print(auth.getToken()['exp'])
    time.sleep(3)
    auth.refreshToken()
    print(auth.getToken()['exp'])
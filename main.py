import asyncio
import logging
import pathlib
import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

executor = ThreadPoolExecutor(8)


class ConsultationRegistration:
    def __init__(self, url: str, user: dict):
        self.url = url
        self.user = user
        self.browser = self.open_browser()

    @staticmethod
    def read_config(config_path: str):
        config = []
        with open(pathlib.Path(config_path)) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for login, password in reader:
                config.append({'login': login, 'password': password})
            logging.log(logging.DEBUG, '', config)
        return config

    @staticmethod
    def open_browser() -> ChromiumDriver:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def disconnect(self):
        self.browser.quit()

    def wait(self, method: any, delay: int = 10):
        print('Wait loading. Delay seconds: ' + str(delay))
        WebDriverWait(self.browser, delay).until(method)

    def try_select_date(self):
        print(self.user['login'], self.user['password'])
        need_repeat = True
        while need_repeat:
            self.browser.get(self.url)
            print('Page loaded')
            self.browser.find_element(By.LINK_TEXT, 'ELEGIR FECHA Y HORA').click()
            print('Go to captcha')
            self.browser.find_element(By.XPATH, '//*[@id="idCaptchaButton"]').click()
            print('Captcha passed')
            try:
                print('Try load time list')
                self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idTimeListTable"]')))
                print('Time list loaded')
                try:
                    self.login_and_select_date()
                    not_available = self.browser.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
                    if type(not_available) is WebElement:
                        print('Not available slots!')
                        need_repeat = False
                        # self.disconnect()
                        time.sleep(10)
                except NoSuchElementException:
                    print('Stub')
            except TimeoutException:
                print('Page loading timeout!')

    def login_and_select_date(self):
        self.browser.find_element(By.LINK_TEXT, 'Cancelar o consultar mis reservas').click()
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idIptBktAccountLoginlogin"]')))
        print('Login form loaded')
        print('Send passport')
        self.browser.find_element(By.XPATH, '//*[@id="idIptBktAccountLoginlogin"]').send_keys(self.user['login'])
        print('Send password')
        self.browser.find_element(By.XPATH, '//*[@id="idIptBktAccountLoginpassword"]').send_keys(self.user['password'])
        print('Login')
        self.browser.find_element(By.XPATH, '//*[@id="idBktDefaultAccountLoginConfirmButton"]').click()
        try:
            repeat = True
            while repeat:
                result = self.has_free_time()
                if result:
                    print('Repeating stopped')
                    repeat = False
                else:
                    print('Wait 3 seconds...')
                    time.sleep(3)

        except NoSuchElementException:
            print('User already registered')
            self.browser.quit()

    def has_free_time(self) -> bool:
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idDivBktAccountHistoryContainer"]')))
        self.browser.find_element(By.XPATH, '//*[@id="idDivBktAccountHistoryContentNoEvents"]')
        self.browser.find_element(By.XPATH, '//*[@id="idBktDefaultAccountHistoryContainer"]/div[1]/a/div').click()
        print('Try load time list')
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idTimeListTable"]')))
        try:
            not_available = self.browser.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
            if type(not_available) is WebElement:
                print('Not available slots! Try again..')
                self.wait(EC.element_to_be_clickable((By.XPATH, '//*[@id="idBktWidgetDefaultFooterAccountSignOutAccountName"]')))
                self.wait(EC.invisibility_of_element_located((By.CLASS_NAME, 'clsDivBktWidgetDefaultLoading')))
                print('Go to history')
                self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Ver historial').click()
                return False
        except NoSuchElementException:
            time.sleep(10)
            print('Slot Available Stub')
            return True


def scrape(url: str, user: dict, *, loop):
    loop.run_in_executor(executor, scraper, url, user)


def scraper(url: str, user: dict):
    print(url, user['login'], user['password'])
    registration = ConsultationRegistration(url, user)
    registration.try_select_date()


if __name__ == '__main__':
    f = open('url.txt')
    url = f.read()
    f.close()
    loop = asyncio.get_event_loop()
    for user in ConsultationRegistration.read_config('clients.csv'):
        scrape(url, user, loop=loop)
    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))

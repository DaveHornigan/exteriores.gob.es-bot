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
        print('Logged in by: ' + self.user['login'])
        need_repeat = True
        while need_repeat:
            self.browser.get(self.url)
            self.wait(EC.visibility_of_element_located((By.LINK_TEXT, 'ELEGIR FECHA Y HORA')))
            self.browser.find_element(By.LINK_TEXT, 'ELEGIR FECHA Y HORA').click()
            print('Go to captcha')
            self.browser.find_element(By.XPATH, '//*[@id="idCaptchaButton"]').click()
            print('Captcha passed')
            try:
                print('Try load time list')
                self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idTimeListTable"]')), 120)
                self.wait(EC.invisibility_of_element_located((By.CLASS_NAME, 'clsDivBktWidgetDefaultLoading')), 120)
                print('Time list loaded')
                self.login()
                try:
                    if self.is_user_already_registered():
                        exit(0)
                    self.find_free_slots()
                    need_repeat = False
                    time.sleep(10)
                except NoSuchElementException:
                    print('Error!')
            except TimeoutException:
                print('Page loading timeout!')

    def login(self):
        self.browser.find_element(By.LINK_TEXT, 'Cancelar o consultar mis reservas').click()
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idIptBktAccountLoginlogin"]')))
        print('Login form loaded')
        print('Send passport')
        self.browser.find_element(By.XPATH, '//*[@id="idIptBktAccountLoginlogin"]').send_keys(self.user['login'])
        print('Send password')
        self.browser.find_element(By.XPATH, '//*[@id="idIptBktAccountLoginpassword"]').send_keys(self.user['password'])
        print('Login')
        self.browser.find_element(By.XPATH, '//*[@id="idBktDefaultAccountLoginConfirmButton"]').click()

    def is_user_already_registered(self) -> bool:
        print('Check user history')
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idDivBktAccountHistoryContainer"]')))
        self.wait(EC.invisibility_of_element_located((By.CLASS_NAME, 'clsDivBktWidgetDefaultLoading')))
        element = self.browser.find_element(By.XPATH, '//*[@id="idDivBktAccountHistoryContentNoEvents"]')
        if element.is_displayed():
            print('User not registered')
            return False
        print('User already registered!')
        return True

    def find_free_slots(self):
        repeat = True
        while repeat:
            result = self.has_free_slots()
            if result:
                print('Repeating stopped. Slot available!')
                repeat = False
                self.try_register_slot()
            else:
                if self.is_user_already_registered():
                    exit(0)
                print('Wait 3 seconds...')
                time.sleep(3)

    def has_free_slots(self) -> bool:
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idDivBktAccountHistoryContainer"]')))
        self.browser.find_element(By.XPATH, '//*[@id="idBktDefaultAccountHistoryContainer"]/div[1]/a/div').click()
        print('Try load time list')
        self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="idTimeListTable"]')))
        try:
            self.wait(EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="idBktWidgetDefaultFooterAccountSignOutAccountName"]'
            )))
            self.wait(EC.invisibility_of_element_located((By.CLASS_NAME, 'clsDivBktWidgetDefaultLoading')), 120)
            self.browser.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
            print('Open calendar')
            self.browser.find_element(By.XPATH, '//*[@id="idDivBktDatetimeDatePickerText"]').click()
            print('Find date with free slots')
            try:
                self.browser.find_element(By.CLASS_NAME, 'clsAvailableSlotsDate').click()
            except NoSuchElementException:
                print('Not available dates with free slots! Wait 3 seconds and try again..')
                time.sleep(3)
                self.browser.find_element(
                    By.XPATH,
                    '//*[@id="idBktWidgetDefaultBodyContainer"]/div[@style="display: block;"]'
                ).click()
                self.browser.find_element(
                    By.XPATH,
                    '//*[@id="idBktWidgetDefaultFooterAccountSignOutAccountName"]'
                ).click()
                return False
            print('Date selected')
            self.browser.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
            print('Not available slots! Try again.. Go to history')
            self.browser.find_element(By.XPATH, '//*[@id="idBktWidgetDefaultFooterAccountSignOutAccountName"]').click()
            return False
        except NoSuchElementException:
            return True

    def try_register_slot(self):
        self.browser.find_element(By.CLASS_NAME, 'clsDivDatetimeSlot').click()
        self.wait(EC.element_to_be_clickable((By.XPATH, '//*[@id="idBktDefaultSignInConfirmButton"]')))
        self.browser.find_element(By.XPATH, '//*[@id="idBktDefaultSignInConfirmButton"]').click()


def scrape(url: str, user: dict, *, loop):
    loop.run_in_executor(executor, scraper, url, user)


def scraper(url: str, user: dict):
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

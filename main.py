import pathlib
import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


class ConsultationRegistration:
    def __init__(self):
        self.url = 'https://bit.ly/379INAI'
        self.configPath = pathlib.Path('./clients.csv')

    def read_config(self):
        with open(self.configPath) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in reader:
                print(', '.join(row))

    @staticmethod
    def open_browser() -> ChromiumDriver:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    @staticmethod
    def disconnect(browser: ChromiumDriver):
        browser.quit()

    @staticmethod
    def wait(browser: ChromiumDriver, delay: int, method: any):
        WebDriverWait(browser, delay).until(method)

    def try_select_date(self):
        browser = self.open_browser()
        need_repeat = True
        while need_repeat:
            browser.get(self.url)
            browser.find_element(By.LINK_TEXT, 'ELEGIR FECHA Y HORA').click()
            browser.find_element(By.XPATH, '//*[@id="idCaptchaButton"]').click()
            delay = 10
            try:
                self.wait(browser, delay, EC.visibility_of_element_located((By.XPATH, '//*[@id="idTimeListTable"]')))
                print('Page loaded!')
                try:
                    not_available = browser.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
                    if type(not_available) is WebElement:
                        print('Not available slots!')
                        need_repeat = False
                        test.disconnect(browser)
                except NoSuchElementException:
                    self.select_date()
            except TimeoutException:
                print('Page loading timeout!')

    def select_date(self):
        print('Stub')

if __name__ == '__main__':
    test = ConsultationRegistration()
    test.read_config()
    test.open_browser()
    test.try_select_date()

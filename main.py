from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class ConsultationRegistration:
    def __init__(self):
        self.url = 'https://bit.ly/379INAI'
        self.driver = None
        self.connect()

    def print_hi(self, name: str):
        print(f'Hi, {name}')

    def connect(self) -> ChromiumDriver:
        self.driver = webdriver.Chrome()

        return self.driver

    def disconnect(self):
        self.driver.quit()

    def try_select_date(self):
        self.driver.get(self.url)
        self.driver.find_element(By.LINK_TEXT, 'ELEGIR FECHA Y HORA').click()
        self.driver.find_element(By.XPATH, '//*[@id="idCaptchaButton"]').click()
        not_available = self.driver.find_element(By.XPATH, '//*[@id="idDivNotAvailableSlotsContainer"]')
        if type(not_available) is WebElement:
            test.disconnect()


if __name__ == '__main__':
    test = ConsultationRegistration()
    test.connect()
    test.try_select_date()

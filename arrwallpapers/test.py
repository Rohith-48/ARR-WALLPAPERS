from datetime import datetime
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Hosttest(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.live_server_url = 'http://127.0.0.1:8000/'

    def tearDown(self):
        self.driver.quit()

    def test_02_registration_and_login(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.maximize_window()
        time.sleep(1)

        # Registration
        registration_link = driver.find_element(By.CSS_SELECTOR, "#premiumsignup")
        registration_link.click()
        time.sleep(2)
        username = driver.find_element(By.CSS_SELECTOR, "input#username")
        username.send_keys("Dony")
        email = driver.find_element(By.CSS_SELECTOR, "input#email")
        email.send_keys("dony2001@gmail.com")
        password = driver.find_element(By.CSS_SELECTOR, "input#password1")
        password.send_keys("NewUser@123")
        confirm_password = driver.find_element(By.CSS_SELECTOR, "input#password2")
        confirm_password.send_keys("NewUser@123")
        signup_button = driver.find_element(By.CSS_SELECTOR, "button#submit")
        signup_button.click()
        time.sleep(2)

        username = driver.find_element(By.CSS_SELECTOR, "input#username")
        username.send_keys("Dony")
        password = driver.find_element(By.CSS_SELECTOR, "input#password")
        password.send_keys("NewUser@123")
        time.sleep(1)
        submitc = driver.find_element(By.CSS_SELECTOR, "button#submit")
        submitc.click()
        time.sleep(2)

        # Perform actions after login (e.g., download)
        driver.get("http://127.0.0.1:8000/wallpaper/46/")
        time.sleep(2)
        submitc = driver.find_element(By.CSS_SELECTOR, "a#download-for-my-screen")
        submitc.click()
        time.sleep(2)

        dropdown_toggle = driver.find_element(By.CLASS_NAME, "dropdown-toggle")
        dropdown_toggle.click()
        time.sleep(1)

        # Find and click the "Logout" link within the dropdown
        submitc = driver.find_element(By.CSS_SELECTOR, "a.logout")
        submitc.click()
        time.sleep(2)

        print("Test done successfully")

if __name__ == '__main__':
    import unittest
    unittest.main()
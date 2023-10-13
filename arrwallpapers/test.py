from datetime import datetime
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class Hosttest(TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.live_server_url = 'http://127.0.0.1:8000/'

    def tearDown(self):
        self.driver.quit()
        
    def test_01_login_page(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.maximize_window()
        time.sleep(1)
        login=driver.find_element(By.CSS_SELECTOR,".login")
        login.click()
        time.sleep(2)
        username=driver.find_element(By.CSS_SELECTOR,"input#username")
        username.send_keys("rohithsanthosh")
        password=driver.find_element(By.CSS_SELECTOR,"input#password")
        password.send_keys("R0hith@12")
        time.sleep(1)
        submitc=driver.find_element(By.CSS_SELECTOR,"button#submit")
        submitc.click()
        time.sleep(2)
        find=driver.find_element(By.CSS_SELECTOR,"a[href='/therapist/listtherapist/']")
        find.click()
        time.sleep(2)
        # search=driver.find_element(By.CSS_SELECTOR,"input#query.form-control.border-primary.w-50")
        # search.send_keys("Abhijith Shaji")\
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#query.form-control.border-primary.w-50")))
        search_input.send_keys("Abhijith")
        time.sleep(5)
        

    # Add more test methods as needed

if __name__ == '__main__':
    import unittest
    unittest.main()
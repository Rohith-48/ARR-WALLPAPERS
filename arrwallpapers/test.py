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
        captcha = driver.find_element(By.CSS_SELECTOR, ".g-recaptcha")
        captcha.click() 
        time.sleep(30)
        submit_button = driver.find_element(By.CSS_SELECTOR, "button#submit")
        submit_button.click()
        time.sleep(2)




        # Perform actions after login (e.g., download)
        driver.get("http://127.0.0.1:8000/wallpaper/46/")
        time.sleep(2)
        submitc = driver.find_element(By.CSS_SELECTOR, "a#download-for-my-screen")
        submitc.click()
        time.sleep(2)

        ai_wallpaper_generator_link = driver.find_element(By.XPATH, "//li[@class='dropdown first']/a[contains(text(),'AI Wallpaper Generator')]")
        ai_wallpaper_generator_link.click()
        time.sleep(2)

        prompt_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.prompt-input")))

        # Clear any existing text in the input field
        prompt_input.clear()

        # Enter the desired text
        prompt_input.send_keys("car on a road")

        # Wait for a short moment to ensure the text is entered before proceeding (optional)
        time.sleep(2)
        # Locate the "Generate" button and click on it
        generate_button = driver.find_element(By.CSS_SELECTOR, "button#generate-btn")
        generate_button.click()
        time.sleep(30)


        driver.get("http://127.0.0.1:8000/")
        time.sleep(2)

        # review_section = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "cont")))
        # actions = ActionChains(driver)
        # actions.move_to_element(review_section).perform()

        # # Wait for the stars to be clickable
        # stars = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.star.star-5")))

        # # Select the 5-star rating
        # star_5 = driver.find_element(By.CSS_SELECTOR, "input.star.star-5")
        # star_5.click()

        # # Enter the review message
        # review_textarea = driver.find_element(By.ID, "review")
        # review_textarea.send_keys("super")

        # # Click the "Post" button
        # post_button = driver.find_element(By.CLASS_NAME, "post-button")
        # post_button.click()

        # # Optional: Add a delay to ensure the review submission completes
        # time.sleep(2)



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






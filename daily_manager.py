from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import date
from datetime import datetime
import math
import json

# Create image directory if not present
image_path = os.getcwd() + "/daily_images"
if not os.path.exists(image_path):
    os.makedirs(image_path)

# Define chromedriver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')

with open('config.json', 'r') as f:
    config = json.load(f)


class DailyManager:

    def __init__(self, username, password):
        """ Instantiate a chrome webdriver to access NDHP daily system"""
        self.today = date.today()
        self.browser = None
        self.image_count = 0
        self.username = username
        self.password = password
        self.build_driver()

    def build_driver(self):
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                        options=options)

    def login(self):
        """ Login to NDHP daily system"""
        self.browser.get(config["ndhp_website"])
        self.browser.find_element(By.NAME, "j_username").send_keys(self.username)
        self.browser.find_element(
            By.NAME, "j_password").send_keys(self.password)
        self.browser.find_element(By.NAME, "login").click()

    def click_monthly(self):
        """ Click monthly daily button from main menu webpage """
        self.browser.find_element(By.LINK_TEXT, "See My Monthly").click()

    def screenshot(self):
        """ Take a screenshot of the current page and save it to current directory in daily_images folder """
        self.browser.save_screenshot(f"daily_images/{self.image_count}.png")
        print(f"Image saved as {self.image_count}.png")
        self.image_count += 1

    def click_next(self):
        """ Click next button from monthly daily webpage """
        self.browser.find_element(By.LINK_TEXT, "Next").click()

    def purge_images(self):
        """ Delete all the image files in the daily_images directory """
        for filename in os.listdir(image_path):
            os.remove(os.path.join(image_path, filename))

    def get_month(self):
        """ Get the text data of the month range from the monthly webpage as a list """
        input_string = self.browser.find_element(By.XPATH,
                                                 '//*[@id="ViewQuickSchedulesFM"]/div[1]/div[1]/div/ul/li[2]').text
        months = [datetime.strptime(date, '%m/%d/%Y').strftime('%m') for date in input_string.split(' - ')]
        return months

    def cycle_screenshot(self, month):
        """ Take screenshots of dailies involving the given months from the monthly webpage """
        if len(month) < 2:  # Format if single digit month
            month = f"0{month}"

        current_month = self.today.month
        month_diff = (int(month) - current_month) % 12
        next_count = month_diff + math.ceil(month_diff / 4)

        if next_count == 0:
            next_count = 2

        print(f"Schedule Requested... cycling {next_count} schedule images.")
        for i in range(next_count):
            month_list = self.get_month()
            if month in month_list:
                self.screenshot()

            self.click_next()

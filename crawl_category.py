import numpy as np
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import random
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
import pandas as pd
import itertools

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
# driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\chromdriv\\chromedriver-win64\\chromedriver.exe" , options=chrome_options)

# driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\crawlDataTraining_selenium\\chromedriver.exe" , options=chrome_options)
# Open URL
class TikiScraper:
    def __init__(self):
        self.driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\chromdriv\\chromedriver-win64\\chromedriver.exe" , options=chrome_options)

    def get_links(self):
        # Mở trang web Tiki
        self.driver.get("https://tiki.vn/")
        sleep(random.randint(2,4))

        # Tìm tất cả các đối tượng chứa link đến trang sản phẩm
        title_elements = self.driver.find_elements(By.CLASS_NAME, 'styles__StyledItem-sc-oho8ay-0.bzmzGe')
        link_elements = title_elements[8:]

        # Lưu trữ các liên kết vào danh sách
        links = [link.get_attribute("href") for link in link_elements]
        links = links[:-1]

        # Đóng trình duyệt
        self.driver.quit()

        # Trả về danh sách liên kết
        return links

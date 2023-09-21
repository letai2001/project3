import numpy as np
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import random
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
import pandas as pd
import itertools
from crawl_category import TikiScraper
import threading
import csv

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

class TikiScraper_link_item:
        def __init__(self):
            self.driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\chromdriv\\chromedriver-win64\\chromedriver.exe" , options=chrome_options)
            self.crawled_links = set()


        def scrape_page_link(self):
            scraper = TikiScraper()
            crawled_links = set()

            with open('product_link_2.csv', 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    crawled_links.add(row['link_item'])
    # Lấy danh sách liên kết
            links = scraper.get_links()
            
            

            MAX_RETRIES = 5
            def scrape_page(links):
                
                for link in links:
                    
                    driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\chromdriv\\chromedriver-win64\\chromedriver.exe" , options=chrome_options)
                    for i in range(0, 10):
                    # Truy cập trang Tiki có chỉ số i
                        
                        if i > 0:
                            driver.get(link + '?page='+ str(i))
                        else: 
                            driver.get(link)
                        sleep(random.randint(1,3))

                        for i in range(MAX_RETRIES):
                            try:
                                elems = driver.find_elements(By.CLASS_NAME , "product-item")
                                break
                            except NoSuchElementException:
                                print(f"Element not found, retrying ({i+1}/{MAX_RETRIES})...")
                                sleep(1)

                        for elem in elems:
                            for i in range(MAX_RETRIES):
                                try:
                                    
                                        
                                    link2  = elem.get_attribute('href')
                                    if link not in self.crawled_links:
                                            self.crawled_links.add(link2)
                                            with open('C:\\Users\\Admin\\Downloads\\crawlDataTraining_selenium\\product_link_2.csv', 'a', encoding='utf-8', newline='') as f:
                                                writer = csv.writer(f)
                                                writer.writerow([link2])
                                    break
                                    
                                except:
                                    print("khong thay href!")
                                    sleep(1)

                            
            scrape_page(links)

    # Bắt đầu chạy các thread



            self.driver.quit()
            
            crawled_link_csv_list = list(self.crawled_links)

            return crawled_link_csv_list
                           
        # elems_prices = driver.find_elements(By.CSS_SELECTOR , ".price-discount__price")
        # for elem_price in elems_prices:
        #     price = elem_price.text
        #     prices.append(elem_price)

# df1 = pd.DataFrame({'link_item': link_item} )
# df1.to_csv('product_link_.csv', index=True)
tiki_link = TikiScraper_link_item()
list = tiki_link.scrape_page_link()
print(list)
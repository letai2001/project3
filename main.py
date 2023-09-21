import numpy as np
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import random
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
import pandas as pd
import itertools
from selenium.common.exceptions import NoSuchElementException
import re
import humanfriendly
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import threading
from queue import Queue
# from crawl import TikiScraper_link_item
import json
from selenium.common.exceptions import TimeoutException
import os


chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

# Tiki_link = TikiScraper_link_item()
# p_link = Tiki_link.scrape_page_link()

MAX_RETRIES = 5
number_of_threads = 8
data = []
def find_rep_shop(driver):
    for j in range(MAX_RETRIES): 
        try:
            rep_chat_ele = driver.find_element(By.CLASS_NAME, "item.chat") 
            if rep_chat_ele is None:
                x = "N/A"
            else:
                try:
                    title_div = rep_chat_ele.find_element(By.CLASS_NAME, "title")
                    span = title_div.find_element(By.TAG_NAME, "span")
                    x = span.get_attribute("textContent")
                    break
                    # shop_follow_list.append(follow)
                except:
                    x = "N/A"
                    break
        except Exception as e:
            print(f"Khong lây dc rep_chat , retrying ({j+1}/{MAX_RETRIES})...!")
            if(j==4):
                    x = "N/A"
            sleep(1)

    return x

def find_follow_shop(driver):
    for j in range(MAX_RETRIES): 
        try:
            shop_follow = driver.find_element(By.CLASS_NAME, "item.normal") 
            if shop_follow is None:
                x = 0
                break
            else:
                try:
                    title_div = shop_follow.find_element(By.CLASS_NAME, "title")
                    span = title_div.find_element(By.TAG_NAME, "span")
                    follow_text = span.get_attribute("textContent")
                    x = humanfriendly.parse_size(follow_text, binary=True)
                    # shop_follow_list.append(follow)
                except:
                    x = 0
                break  # thoát vòng lặp nếu đã xác định được giá trị của bi
        except Exception as e:
            print(f"Khong lây dc shop_follow , retrying ({j+1}/{MAX_RETRIES})...!")
            if(j==4):
                    x  = 0
            sleep(1)

    return x

def find_rate_shop(driver):
    x = 0
    for j in range(MAX_RETRIES): 
        try:
            item_review_elements = driver.find_elements(By.CLASS_NAME, "item.review")
            if item_review_elements:
                item_review = item_review_elements[0]
                title_div = item_review.find_element(By.CLASS_NAME, "title")
                span = title_div.find_element(By.TAG_NAME, "span")
                rating_text = span.get_attribute("textContent")
                match = re.search(r"\d+\.\d+", rating_text)
                if match:
                    x = float(match.group())
                break  # thoát vòng lặp nếu đã xác định được giá trị của biến
            else:
                break  # thoát vòng lặp nếu không tìm thấy phần tử
        except Exception as e: 
            print(f"khong thay phan tu item_review , retrying ({j+1}/{MAX_RETRIES})...")
            sleep(1)
    return x
def find_quantity_sold(driver ,xpath ):
    for j in range(3):            
            try: 
                quantity_sold = driver.find_element(By.XPATH, xpath)
            
                if quantity_sold is not None:
                    x = quantity_sold.get_attribute("innerText").split()[2]
                else :
                    x  = 0
                break  # thoát vòng lặp nếu đã xác định được giá trị của biến
            except Exception as e:
                print(f"khong thay phan tu quantitysold , retrying ({j+1}/{MAX_RETRIES})...")
                if(j==2):
                    x = 0
                sleep(1)
    return x
def find_ele(driver , class_name):
    for j in range(MAX_RETRIES):
            try:
                    
                    element = driver.find_element(By.CLASS_NAME , class_name)
                    if element is not None:
                        x = element.text
                    else :
                        x  = 0
                    break   
            except Exception:
                    print(f"Element not found, retrying ({j+1}/{MAX_RETRIES})...")
                    if(j==4):
                        x = 0
                    height = driver.execute_script("return document.documentElement.scrollHeight")
                    if class_name == "review-images__heading" :
                        driver.execute_script("window.scrollBy(0, {});".format(int(height * (0.4+j*0.1))))
                    sleep(1.5*j)
    return x

def find_rating(driver , classname):    
    for j in range(3):
            try:
                    height = driver.execute_script("return document.documentElement.scrollHeight")
                    wait = WebDriverWait(driver, 5)
                    sleep(4)
                    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, classname )))
                    if element is not None:
                        x = element.text
                    else :
                        x  = 0
                    break 
            except Exception:
                    print(f"Element rating_point_ele or image  not found, retrying ({j+1}/{MAX_RETRIES+1})...")
                    if(j==2):
                        x = 0
                   
                    driver.execute_script("window.scrollBy(0, {});".format(int(height * (0.4+j*0.1))))
                    sleep(2*j)
    return x

lock = threading.Lock()
visited_links_lock  = threading.Lock()
queue_lock = threading.Lock()
visited_links = set()
# Open the JSON file for reading

try:
    with open('datarate.json', 'r') as f:
        for line in f:
            obj = json.loads(line)
            visited_links.add(obj['link'])
except json.decoder.JSONDecodeError as e:
    print(f'Lỗi phân tích JSON: {e}')
def get_data_from_link(queue , lock , visited_links_lock , queue_lock):
    driver = webdriver.Chrome("C:\\Users\\Admin\\Downloads\\chromdriv\\chromedriver-win64\\chromedriver.exe" , options=chrome_options)
    
    while(True):
            with queue_lock:
                link = queue.get()
            
            if link is None:
                break
            if link not in visited_links:
                    driver.get(link)
                    sleep(2)
                    price = find_ele(driver , "product-price__current-price")
                    # discount = find_ele(driver , "product-price__discount-rate")
                    # review_count = find_ele(driver , "number")
                    # count_code = find_ele(driver , "coupon__text")
                    sold_number = find_quantity_sold(driver, "//div[@data-view-id='pdp_quantity_sold']" )
                    
                    height = driver.execute_script("return document.documentElement.scrollHeight")
                        # # Cuộn trang xuống 1/3 chiều cao của trang
                    # driver.execute_script("window.scrollBy(0, {});".format(int(height * 0.15)))
                    #     # html = driver.find_element(By.TAG_NAME, 'html')
                    #     # html.send_keys(Keys.END) 
                    # sleep(4)
                    # rating = find_rate_shop(driver)
                    # follow = find_follow_shop(driver)
                    # rep_chat_text = find_rep_shop(driver)

                    driver.execute_script("window.scrollBy(0, {});".format(int(height * 0.4))) 
                    sleep(2.5)
                    # rating = find_rate_shop(driver)
                    # # follow = find_follow_shop(driver)
                    # # rep_chat_text = find_rep_shop(driver)

                    
                    driver.execute_script("window.scrollBy(0, {});".format(int(height * 0.6))) 


                    sleep(2.5)

                    # number_image = find_ele(driver , "review-images__heading")
                    rating_point = find_rating(driver, "review-rating__point")
                   
                    data.append({"link": link, "price": price, "quantity_sold":sold_number ,   
                            "rating_avarage": rating_point})
                    
            
                    with visited_links_lock:
                        visited_links.add(link)
        # Ghi dữ liệu vào file JSON
                    with lock:
                        with open('datarate.json', 'a') as f:
                            json.dump(data[-1], f)
                            f.write('\n')

        # df = pd.DataFrame(data, columns=['Link', 'Price', 'Discount', 'Number of Ratings', 'Number of Reviews', 'Store Rating', 'Number of Store Followers', 'Available Coupons', 'Average Rating'])
def main():
    df_link = pd.read_csv('data_final.csv')
# TSC = TikiScraper_link_item()
# df_link = TSC.scrape_page_link()

    p_link = df_link['link'].to_list()
     
    

    queue = Queue()
    for link in p_link:
        queue.put(link)
    for i in range(number_of_threads):
        queue.put(None)
    threads = []

    for i in range(number_of_threads):
        t = threading.Thread(target=get_data_from_link, args=(queue, lock, visited_links_lock , queue_lock ,))
        threads.append(t)

    # Bắt đầu chạy các thread
    for t in threads:  
        t.start()

    # Đợi cho tất cả các thread hoàn thành công việc
    for t in threads:
        t.join()
if __name__ == "__main__":
    main()

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import threading
import os
import pandas as pd
from random import uniform, choice
from click import auto_click
import config


if not os.path.exists('csv.csv'):
    print("Hãy đảm bảo file excel tồn tại")
    time.sleep(10)
    exit()

df = pd.read_csv('csv.csv')
list_link = df["Link"].dropna().values.tolist()

driver_lock = threading.Lock()
confirmation_received = threading.Event()

def main(idx):
    options = uc.ChromeOptions()
    profile_directory = f"Profile_{idx}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        try:
            options.user_data_dir = profile_directory
            driver = uc.Chrome(options=options)
        except Exception:
            print(f"Lỗi 1 ở luồng {idx + 1}")
            time.sleep(180)
            return

    driver.maximize_window()

    driver.get("https://www.facebook.com/")

    confirmation_received.wait()
    
    for link in list_link:
        driver.get(link + "/members")
        
        try:
            target_list = driver.find_element(By.XPATH, '//div[@role="list"][.//span[contains(text(), "New to the group")]]')
            members = driver.find_elements(By.XPATH, '//div[@role="listitem"]')
        except:
            target_list = None  # Nếu không tìm thấy
            print("ko")


threads = []

quantity = 1  # input("Nhập số lượng luồng: ")
for idx in range(int(quantity)):
    thread = threading.Thread(target=main, args=(idx,))
    thread.start()
    threads.append(thread)

start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình spam: ")
if start_program.lower() == "ok":
    confirmation_received.set()

for thread in threads:
    thread.join()

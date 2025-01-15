import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import threading
import os
import pandas as pd
from random import uniform
from click import auto_click


driver_lock = threading.Lock()
confirmation_received = threading.Event()


def main(idx):

    options = uc.ChromeOptions()
    profile_directory = f"Profile_{idx}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        options.user_data_dir = profile_directory
        try:
            driver = uc.Chrome(options=options)
        except Exception:
            print(f"Lỗi 1 ở luồng {idx + 1}")
            time.sleep(180)
            exit()

    driver.maximize_window()

    driver.get("https://chat.zalo.me/")

    if input() == "ok":
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "conversationList")))
        except Exception as e:
            print(f"Lỗi 2 ở luồng {idx + 1}")
            driver.quit()
            return

        chat_items = driver.find_elements(By.XPATH, '//div[@id="conversationList"]//div[contains(@class, "msg-item")]')
        print(f"Số lượng đoạn chat: {len(chat_items)}")

        for idx, chat in enumerate(chat_items):
            chat.click()

            ActionChains(driver).send_keys(f"Tin nhắn số {idx}").perform()

            print(f"Đã gửi tin nhắn cho đoạn chat {idx + 1}.")

        time.sleep(1000)


main(1)

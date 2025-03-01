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


if not os.path.exists('link_post.csv') or not os.path.exists('text.csv'):
    print("Hãy đảm bảo file excel tồn tại")
    time.sleep(10)
    exit()

df_link_post = pd.read_csv('link_post.csv')
list_link_post = df_link_post["Link"].dropna().values.tolist()

df_status = pd.read_csv('link_post.csv')
list_status = df_status["Status"].dropna().values.tolist()

df_text = pd.read_csv('text.csv')
list_text = df_text["Text"].dropna().values.tolist()


driver_lock = threading.Lock()
file_lock = threading.Lock()
confirmation_received = threading.Event()


def main(idx):
    options = uc.ChromeOptions()
    profile_directory = f"Profile_{idx + 1}"
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

    # screen_width = driver.execute_script("return window.screen.availWidth;")
    # screen_height = driver.execute_script("return window.screen.availHeight;")
    # window_width = screen_width // 3
    # window_height = screen_height // 2
    # position_x = idx * window_width // 20
    # position_y = 0

    # driver.set_window_size(window_width, window_height)
    # driver.set_window_position(position_x, position_y)
    driver.maximize_window()

    driver.get("https://www.facebook.com/")

    confirmation_received.wait()

    for idx, link in enumerate(list_link_post):
        
        if list_status[idx] == 1:
            continue
        
        driver.get(link)
        time.sleep(uniform(1, 3))

        # while True:
        #     last_height = driver.execute_script("return document.body.scrollHeight")
        #     driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        #     time.sleep(1)
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break

        # try:
        #     WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.feed_xpath)))
        #     posts = driver.find_elements(By.XPATH, config.feed_xpath)[1:]
        # except Exception:
        #     print(f"Lỗi 2 ở luồng {idx + 1}")
        #     continue

        # for post in posts:
        #     try:
        #         driver.execute_script("arguments[0].scrollIntoView(true);", post)
        #         time.sleep(uniform(1, 3))
        #     except Exception:
        #         print(f"Lỗi 3 ở luồng {idx + 1}")
        #         continue

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.comment_button_xpath))
            ).click()
        except Exception:
            print(f"Lỗi 4 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, config.text_box_xpath))
            )
        except Exception:
            print(f"Lỗi 5 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))

        try:
            text = choice(list_text)
            ActionChains(driver).send_keys(text).send_keys(Keys.ENTER).perform()
            time.sleep(uniform(1, 3))
        except Exception:
            print(f"Lỗi 6 ở luồng {idx + 1}")
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                continue
            except Exception:
                print(f"Lỗi 7 ở luồng {idx + 1}")
                continue
        time.sleep(uniform(1, 3))

        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            print(f"Lỗi 7 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))
        
        try:
            df_status.loc[df_status["Link"] == link, "Status"] = 1
            with file_lock:
                df_status.to_csv('link_post.csv', index=False)
        except Exception:
            print(f"Lỗi 8 ở luồng {idx + 1}")
            continue


threads = []

quantity = 1  # input("Nhập số lượng luồng: ")
for idx in range(int(quantity)):
    thread = threading.Thread(target=main, args=(idx,))
    thread.start()
    threads.append(thread)

start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình spam: ")
if start_program.lower().strip() == "ok":
    confirmation_received.set()

for thread in threads:
    thread.join()

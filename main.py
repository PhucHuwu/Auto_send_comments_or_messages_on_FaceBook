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
list_text = df["Text"].dropna().values.tolist()


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

    for link in list_link:
        driver.get(link)
        time.sleep(uniform(1, 3))

        max_scroll_attempts = 1
        for _ in range(max_scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(uniform(1, 3))

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@role="feed"]/div')))
            posts = driver.find_elements(By.XPATH, '//div[@role="feed"]/div')[1:]
        except Exception:
            print(f"Lỗi 2 ở luồng {idx + 1}")
            continue

        for post in posts:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(uniform(1, 3))
            except Exception:
                print(f"Lỗi 3 ở luồng {idx + 1}")
                continue

            try:
                WebDriverWait(post, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Viết bình luận"]'))
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
                time.sleep(uniform(2, 5))
            except Exception:
                print(f"Lỗi 6 ở luồng {idx + 1}")
                try:
                    auto_click(driver, config.close_button_xpath, 30)
                    continue
                except Exception:
                    print(f"Lỗi 7 ở luồng {idx + 1}")
                    continue
            time.sleep(uniform(1, 3))

            try:
                auto_click(driver, config.close_button_xpath, 30)
            except Exception:
                print(f"Lỗi 7 ở luồng {idx + 1}")
                continue

            time.sleep(uniform(1, 3))
    # -----------------------------------------------------------------------------------------------------------------

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

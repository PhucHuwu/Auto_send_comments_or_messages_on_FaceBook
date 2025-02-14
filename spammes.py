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

    driver.maximize_window()

    driver.get("https://www.facebook.com/")

    confirmation_received.wait()
    
    for link in list_link:
        driver.get(link + "/members")

        max_scroll_attempts = 1
        for _ in range(max_scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(uniform(1, 3))

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.list_item_xpath)))
            members = driver.find_elements(By.XPATH, config.list_item_xpath)
        except Exception:
            print(f"Lỗi 2 ở luồng {idx + 1}")
            continue

        for member in members:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", member)
            except Exception:
                print(f"Lỗi 3 ở luồng {idx + 1}")
                continue

            try:
                profile_element = member.find_element(By.XPATH, ".//a[@href]")
                profile_link = profile_element.get_attribute("href")
                driver.execute_script("window.open(arguments[0], '_blank');", profile_link)

                WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])
            except Exception:
                print(f"Lỗi 4 ở luồng {idx + 1}")
                continue

            try:
                auto_click(driver, config.message_button_xpath, 15, 1)
            except Exception:
                print(f"Lỗi 5 ở luồng {idx + 1}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            time.sleep(uniform(1, 3))

            try:
                text = choice(list_text)
                auto_click(driver, config.message_text_box_xpath, 15, 1)
                time.sleep(uniform(1, 3))
                ActionChains(driver).send_keys(text).send_keys(Keys.ENTER).perform()
            except Exception:
                print(f"Lỗi 6 ở luồng {idx + 1}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

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

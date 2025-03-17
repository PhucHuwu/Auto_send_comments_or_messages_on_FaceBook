import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import pandas as pd
import cfg.config as config
from cfg.click import auto_click


if not os.path.exists("file/link_nhom_dang_bai.csv"):
    data = {
        "Link": [],
        "Status": []
    }
    df = pd.DataFrame(data)
    df.to_csv("file/link_nhom_dang_bai.csv", index=False)


driver_lock = threading.Lock()
file_lock = threading.Lock()
confirmation_received = threading.Event()


def save_link_group(link_group):
    clean_link = link_group.split('?')[0]

    with file_lock:
        df = pd.read_csv("file/link_nhom_dang_bai.csv")

        if clean_link not in df["Link"].values:
            new_data = pd.DataFrame({"Link": [clean_link], "Status": [0]})
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv("file/link_nhom_dang_bai.csv", index=False)
        else:
            pass


def main(idx, key):
    options = uc.ChromeOptions()
    options.add_argument("--password-store=basic")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    profile_directory = f"Profile_{idx + 1}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        try:
            options.user_data_dir = profile_directory
            driver = uc.Chrome(options=options)
        except:
            print(f"Lỗi 1 ở luồng {idx + 1}")
            time.sleep(180)
            return

    screen_width = driver.execute_script("return window.screen.availWidth;")
    screen_height = driver.execute_script("return window.screen.availHeight;")
    window_width = screen_width // 5
    window_height = screen_height
    position_x = idx * window_width // 20
    position_y = 0

    driver.set_window_size(window_width, window_height)
    driver.set_window_position(position_x, position_y)
    # driver.maximize_window()

    driver.execute_script("document.body.style.zoom='100%'")
    driver.get("https://www.facebook.com/")
    confirmation_received.wait()
    
    key = key.replace(" ", "+")
    driver.get(f"https://www.facebook.com/search/groups/?q={key}&locale=vi-VN")
    
    auto_click(driver, config.filter_public_group_xpath, 5, 1)
    
    driver.execute_script("document.body.style.zoom='50%'")
    
    collected_groups = set()

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.feed_xpath)))
            groups = driver.find_elements(By.XPATH, config.feed_xpath)
        except:
            print(f"Lỗi 2 ở luồng {idx + 1}")
            break

        new_groups = []
        for group in groups:
            try:
                href_element = group.find_element(By.XPATH, ".//a[@href]")
                link_group = href_element.get_attribute("href")

                if link_group not in collected_groups:
                    collected_groups.add(link_group)
                    new_groups.append(link_group)
            except:
                continue

        for link_group in new_groups:
            save_link_group(link_group)

        if new_height == last_height:
            break


list_key = ["google ads", "quảng cáo google", "seo"]
threads = []

for idx, key in enumerate(list_key):
    thread = threading.Thread(target=main, args=(idx, key))
    thread.start()
    time.sleep(1)
    threads.append(thread)

start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình cào data: ")
if start_program.lower().strip() == "ok":
    confirmation_received.set()

for thread in threads:
    thread.join()

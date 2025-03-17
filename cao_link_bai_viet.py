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
import requests
import pyperclip
from random import uniform
import cfg.config as config
from cfg.click import auto_click


if not os.path.exists('file/link_nhom.csv'):
    print("Hãy đảm bảo file excel tồn tại")
    time.sleep(10)
    exit()

if not os.path.exists("file/link_bai_viet.csv"):
    data = {
        "Link": [],
        "Status": [],
    }
    df = pd.DataFrame(data)
    df.to_csv("file/link_bai_viet.csv", index=False)

df = pd.read_csv('file/link_nhom.csv')
list_link_group = df["Link"].dropna().values.tolist()


driver_lock = threading.Lock()
file_lock = threading.Lock()
confirmation_received = threading.Event()


def save_post_link(link_post):
    if "permalink/" in link_post:
        link_post = link_post.split("permalink/")[0] + "permalink/" + link_post.split("permalink/")[1].split("/")[0] + "/"

    with file_lock:
        if os.path.exists("file/link_bai_viet.csv"):
            df_old = pd.read_csv("file/link_bai_viet.csv")
        else:
            df_old = pd.DataFrame(columns=["Link", "Status"])

        if link_post not in df_old["Link"].values:
            new_data = pd.DataFrame([{"Link": link_post, "Status": 0}])
            df_new = pd.concat([df_old, new_data], ignore_index=True)
            df_new.to_csv("file/link_bai_viet.csv", index=False)


def main(idx, link_group):
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
    driver.get(link_group + "?locale=vi-VN")
    driver.execute_script("document.body.style.zoom='25%'")

    scroll_times = 100
    print(f"Chương trình sẽ thực hiện cuộn trang {scroll_times} lần để load hết các bài viết sau đó mới lưu link")
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        scroll_times -= 1
        print(f"Số lần cuộn còn lại: {scroll_times}")
        if new_height == last_height or scroll_times == 0:
            break

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.feed_xpath)))
        posts = driver.find_elements(By.XPATH, config.feed_xpath)[1:]
    except:
        print(f"Lỗi 2 ở luồng {idx + 1}")
        return

    for post in posts:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", post)
            time.sleep(uniform(1, 3))
        except:
            print(f"Lỗi 3 ở luồng {idx + 1}")
            continue

        try:
            WebDriverWait(post, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.share_button_xpath))
            ).click()
        except:
            print(f"Lỗi 4 ở luồng {idx + 1}")
            continue
        time.sleep(1)

        if not auto_click(driver, config.copy_link_button_xpath, 30):
            print(f"Lỗi 5 ở luồng {idx + 1}")
            continue

        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except:
            print(f"Lỗi 6 ở luồng {idx + 1}")
            continue

        link_post = pyperclip.paste()
        try:
            link_post = requests.get(link_post, allow_redirects=True)
            save_post_link(link_post.url)
        except:
            print(f"Lỗi 6 ở luồng {idx + 1}")


threads = []

for idx, link_group in enumerate(list_link_group):
    thread = threading.Thread(target=main, args=(idx, link_group))
    thread.start()
    time.sleep(1)
    threads.append(thread)

start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình cào data: ")
if start_program.lower().strip() == "ok":
    confirmation_received.set()

for thread in threads:
    thread.join()

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import pandas as pd
import config


if not os.path.exists('link_nhom.csv'):
    print("Hãy đảm bảo file excel tồn tại")
    time.sleep(10)
    exit()
    
if not os.path.exists("link_facebook.csv"):
    data = {
        "Link": [],
        "Status": [],
        "User_ID": []
    }
    df = pd.DataFrame(data)
    df.to_csv("link_facebook.csv", index=False)

df = pd.read_csv('link_nhom.csv')
list_link_group = df["Link"].dropna().values.tolist()


driver_lock = threading.Lock()
file_lock = threading.Lock()
confirmation_received = threading.Event()


def save_user_link(user_links):
    if not user_links:
        return

    pattern = r"https://www\.facebook\.com/groups/\d+/user/(\d+)/"

    if isinstance(user_links, str):
        user_links = [user_links]

    df_new = pd.DataFrame({"Link": user_links, "Status": [0] * len(user_links)})
    df_new["User_ID"] = df_new["Link"].str.extract(pattern)

    df_new = df_new[df_new["User_ID"].notna()].drop_duplicates(subset=["User_ID"])

    if not df_new.empty:
        with file_lock:
            if os.path.exists("link_facebook.csv"):
                df_old = pd.read_csv("link_facebook.csv")
                df_new = pd.concat([df_old, df_new]).drop_duplicates(subset=["User_ID"], keep="first")

            df_new["User_ID"] = df_new["User_ID"].astype(int)
            df_new = df_new.sort_values(by=["User_ID"])
            df_new.to_csv("link_facebook.csv", index=False, mode='w')


def main(idx, link_group):
    options = uc.ChromeOptions()
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
    window_width = screen_width // 3
    window_height = screen_height // 2
    position_x = idx * window_width // 20
    position_y = 0

    driver.set_window_size(window_width, window_height)
    driver.set_window_position(position_x, position_y)
    # driver.maximize_window()

    driver.execute_script("document.body.style.zoom='100%'")
    driver.get("https://www.facebook.com/")
    confirmation_received.wait()
    driver.get(link_group + "/members/?locale=vi-VN")
    driver.execute_script("document.body.style.zoom='25%'")
    collected_users = set()

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.list_item_xpath)))
            members = driver.find_elements(By.XPATH, config.list_item_xpath)
        except:
            print(f"Lỗi 2 ở luồng {idx + 1}")
            break
        
        new_users = []
        for member in members:
            try:
                href_element = member.find_element(By.XPATH, ".//a[@href]")
                user_link = href_element.get_attribute("href")
                
                if user_link not in collected_users:
                    collected_users.add(user_link)
                    new_users.append(user_link)
            except:
                continue
        
        for user_link in new_users:
            save_user_link(user_link)
        
        if new_height == last_height:
            break

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

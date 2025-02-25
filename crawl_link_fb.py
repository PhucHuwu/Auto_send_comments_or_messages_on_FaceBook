import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import threading
import os
import pandas as pd
import config


if not os.path.exists('link_group.csv'):
    print("Hãy đảm bảo file excel tồn tại")
    time.sleep(10)
    exit()

df = pd.read_csv('link_group.csv')
list_link_group = df["Link"].dropna().values.tolist()
list_link_user = []


driver_lock = threading.Lock()
confirmation_received = threading.Event()


def main(idx, link_group):
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

    screen_width = driver.execute_script("return window.screen.availWidth;")
    screen_height = driver.execute_script("return window.screen.availHeight;")
    window_width = screen_width // 3
    window_height = screen_height // 2
    position_x = idx * window_width // 20
    position_y = 0

    driver.set_window_size(window_width, window_height)
    driver.set_window_position(position_x, position_y)
    # driver.maximize_window()

    driver.get("https://www.facebook.com/")

    confirmation_received.wait()

    # for link_group in list_link_group:
    driver.get(link_group + "/members")

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, config.list_item_xpath)))
        members = driver.find_elements(By.XPATH, config.list_item_xpath)
    except Exception:
        print(f"Lỗi 2 ở luồng {idx + 1}")
        # continue

    for member in members:
        try:
            href_element = member.find_element(By.XPATH, ".//a[@href]")
            list_link_user.append(href_element.get_attribute("href"))
        except Exception:
            print(f"Lỗi 3 ở luồng {idx + 1}")
            continue


threads = []

# quantity = 1  # input("Nhập số lượng luồng: ")
# for idx in range(int(quantity)):
#     thread = threading.Thread(target=main, args=(idx,))
#     thread.start()
#     threads.append(thread)

for idx, link_group in enumerate(list_link_group):
    thread = threading.Thread(target=main, args=(idx, link_group))
    thread.start()
    threads.append(thread)

start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình spam: ")
if start_program.lower().strip() == "ok":
    confirmation_received.set()

for thread in threads:
    thread.join()

df = pd.DataFrame({
    "Link": list_link_user,
    "Status": 0
})

pattern = r"https://www\.facebook\.com/groups/\d+/user/\d+/"
df["User_ID"] = df["Link"].str.extract(pattern)
df = df.drop_duplicates(subset=["User_ID"], keep="first")
df = df.drop(columns=["User_ID"])
df = df[df["Link"].str.match(pattern, na=False)]
df.to_csv('link_user.csv', index=False)

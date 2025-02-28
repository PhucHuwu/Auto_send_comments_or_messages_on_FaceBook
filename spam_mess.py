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


if not os.path.exists('link_user.csv'):
    print("Vui lòng chạy tool cào link fb trước")
    time.sleep(30)
    exit()

df_link_user = pd.read_csv('link_user.csv')
list_link_user = df_link_user["Link"].dropna().values.tolist() # danh sách link user
list_status = df_link_user["Status"].dropna().values.tolist() # trạng thái đã nhắn tin hay chưa

df_list_text = pd.read_csv('text.csv')
list_text = df_list_text["Text"].dropna().values.tolist() # danh sách kịch bản nhắn tin

df_list_via = pd.read_csv('via.csv')
list_via = df_list_via["Via"].dropna().values.tolist() # danh sách tài khoản via

if len(list_text) == 0:
    print("Vui lòng thêm kịch bản vào file text.csv")
    time.sleep(10)
    exit()


driver_lock = threading.Lock()


def main(idx):
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
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

    # -----------------------------------------------------------------------------------------------------------------
    for idx, link in enumerate(list_link_user):

        if list_status[idx] == 1: # nếu đã nhắn tin rồi thì bỏ qua
            continue

        driver.get("https://www.facebook.com/")
        time.sleep(uniform(1, 3))

        # dang nhap

        driver.get(link)

        # Nhắn tin ----------------------------------------------------------------------------------------------------
        try:
            auto_click(driver, config.message_button_xpath, 15, 1) # click vào nút nhắn tin
        except Exception:
            print(f"Lỗi 5 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))

        try:
            auto_click(driver, config.message_text_box_xpath, 15, 1) # click vào ô nhập tin nhắn
        except Exception:
            print(f"Lỗi 6 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))

        try:
            text = choice(list_text)
            ActionChains(driver).send_keys(text).send_keys(Keys.ENTER).perform() # nhập tin nhắn và gửi
        except Exception:
            print(f"Lỗi 7 ở luồng {idx + 1}")
            continue
        time.sleep(uniform(1, 3))

        list_status[idx] = 1  # cập nhật trạng thái đã nhắn tin
        df_link_user["Status"] = list_status
        df_link_user.to_csv('link_user.csv', index=False)
        # -------------------------------------------------------------------------------------------------------------


threads = []

quantity = 1  # input("Nhập số lượng luồng: ")
for idx in range(int(quantity)):
    thread = threading.Thread(target=main, args=(idx,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

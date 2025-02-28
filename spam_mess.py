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
from random import uniform, choice
from click import auto_click
import config


if not os.path.exists('link_user.csv'):
    print("Vui lòng chạy tool cào link fb trước")
    time.sleep(30)
    exit()

df_link_user = pd.read_csv('link_user.csv')
list_link_user = df_link_user["Link"].dropna().values.tolist()
list_status = df_link_user["Status"].dropna().values.tolist()

df_list_text = pd.read_csv('text.csv')
list_text = df_list_text["Text"].dropna().values.tolist()

df_list_via = pd.read_csv('via.csv')
list_via = df_list_via["Via"].dropna().values.tolist()

if len(list_text) == 0:
    print("Vui lòng thêm kịch bản vào file text.csv")
    time.sleep(10)
    exit()

max_messages_per_via = 20
num_threads = 2 # min(len(list_via), len(list_link_user) // max_messages_per_via, os.cpu_count())

chunks = [list_link_user[i::num_threads] for i in range(num_threads)]
status_chunks = [list_status[i::num_threads] for i in range(num_threads)]

driver_lock = threading.Lock()
file_lock = threading.Lock()


def get_token(two_fa_token):
    url = "https://2fa.live/tok/" + two_fa_token
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        token = data["token"]
    return token


def is_logged_out(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email"]'))
        )
        return True
    except:
        return False


def log_in(driver, thread_id, via_index):
    list_via_split = list_via[via_index].split('|')
    account_id, password, two_fa_token = list_via_split[0], list_via_split[1], get_token(list_via_split[2])

    time.sleep(3)
    if two_fa_token is None:
        via_index += num_threads
        return False

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email"]'))
        ).click()
    except:
        print(f"Lỗi 4 ở luồng {thread_id + 1}")
        return False

    try:
        ActionChains(driver).send_keys(account_id).send_keys(Keys.TAB).perform()
        ActionChains(driver).send_keys(password).send_keys(Keys.ENTER).perform()
    except:
        print(f"Lỗi 5 ở luồng {thread_id + 1}")
        return False
    time.sleep(uniform(1, 3))

    try:
        ActionChains(driver).send_keys(two_fa_token).send_keys(Keys.ENTER).perform()
    except:
        print(f"Lỗi 6 ở luồng {thread_id + 1}")
    time.sleep(uniform(1, 3))

    try:
        auto_click(driver, config.trust_device_button_xpath, 5, 1)
    except:
        print(f"Lỗi 7 ở luồng {thread_id + 1}")

    # if "checkpoint" in driver.current_url:
    #     try:
    #         auto_click(driver, config.checkpoint_account_logout_button_xpath, 5, 1)
    #         auto_click(driver, config.logout_button_xpath, 5, 1)
    #     except:
    #         print(f"Lỗi 11 ở luồng {thread_id + 1}")
    #     via_index += num_threads
    #     return False
    
    return True


def main(thread_id, user_chunk, status_chunk):
    options = uc.ChromeOptions()
    profile_directory = f"Profile_{thread_id + 1}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        try:
            options.user_data_dir = profile_directory
            driver = uc.Chrome(options=options)
        except Exception:
            print(f"Lỗi 1 ở luồng {thread_id + 1}")
            time.sleep(180)
            return

    screen_width = driver.execute_script("return window.screen.availWidth;")
    screen_height = driver.execute_script("return window.screen.availHeight;")
    window_width = screen_width // 3
    window_height = screen_height // 2
    position_x = thread_id * window_width // 20
    position_y = 0

    driver.set_window_size(window_width, window_height)
    driver.set_window_position(position_x, position_y)
    # driver.maximize_window()

    messages_sent = 0
    via_index = thread_id

    # -----------------------------------------------------------------------------------------------------------------
    while via_index < len(list_via):
        driver.get("https://www.facebook.com/")
        time.sleep(3)

        if is_logged_out(driver):
            if not log_in(driver, thread_id, via_index):
                continue
        else:
            try:
                auto_click(driver, config.your_profile_button_xpath, 5, 1)
            except Exception:
                # try:
                #     auto_click(driver, config.checkpoint_account_logout_button_xpath, 5, 1)
                # except Exception:
                    # print(f"Lỗi 2 ở luồng {thread_id + 1}")
                    # continue
                print(f"Lỗi 2 ở luồng {thread_id + 1}")
                continue
            
            try:
                auto_click(driver, config.logout_button_xpath, 5, 1)
            except Exception:
                print(f"Lỗi 3 ở luồng {thread_id + 1}")
                continue
            
            if not log_in(driver, thread_id, via_index):
                continue

        for idx, link in enumerate(user_chunk):
            if status_chunk[idx] == 1:
                continue

            if messages_sent >= max_messages_per_via:
                break

            driver.get(link)
            time.sleep(uniform(1, 3))

            try:
                auto_click(driver, config.message_button_xpath, 15, 1)
            except Exception:
                print(f"Lỗi 8 ở luồng {thread_id + 1}")
                continue
            time.sleep(uniform(1, 3))

            try:
                auto_click(driver, config.message_text_box_xpath, 15, 1)
            except Exception:
                print(f"Lỗi 9 ở luồng {thread_id + 1}")
                continue
            time.sleep(uniform(1, 3))

            try:
                text = choice(list_text)
                ActionChains(driver).send_keys(text).send_keys(Keys.ENTER).perform()
                time.sleep(1)

                sent_message_xpath = f'//div[contains(text(), "{text}")]'
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, sent_message_xpath))
                )
                messages_sent += 1
                status_chunk[idx] = 1
                with driver_lock:
                    df_link_user["Status"] = [item for sublist in status_chunks for item in sublist]
                    df_link_user.to_csv('link_user.csv', index=False)

            except Exception:
                print(f"Lỗi 10 ở luồng {thread_id + 1}")
                continue
            time.sleep(uniform(1, 3))

        via_index += num_threads
        messages_sent = 0

        if via_index >= len(list_via):
            return

    if messages_sent == 0:
        print(f"Không gửi được tin nào ở luồng {thread_id + 1}, đóng trình duyệt.")
        driver.quit()
        return


threads = []
for idx in range(num_threads):
    thread = threading.Thread(target=main, args=(idx, chunks[idx], status_chunks[idx]))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

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


if not os.path.exists('link_bai_viet.csv'):
    print("Vui lòng chạy tool cào link bài viết trước")
    time.sleep(30)
    exit()

df_link_post = pd.read_csv('link_bai_viet.csv')
list_link_post = df_link_post["Link"].dropna().values.tolist()
list_status = df_link_post["Status"].dropna().values.tolist()

if sum(list_status) == len(list_link_post):
    print("Tất cả bài viết đã được spam, vui lòng chạy tool để cào link bài viết mới")
    time.sleep(10)
    exit()

with open('kich_ban.txt', 'r', encoding='utf-8') as file:
    list_text = file.read().splitlines()

if len(list_text) == 0:
    print("Vui lòng thêm kịch bản vào file kich_ban.txt")
    time.sleep(10)
    exit()

df_list_via = pd.read_csv('via.csv')
df_list_via = df_list_via[~df_list_via["Status"].isin(["Checkpoint", "Invalid", "Wrong password"])]
list_via = df_list_via["Via"].dropna().tolist()
list_status_via = df_list_via["Status"].dropna().tolist()

if len(list_via) == 0:
    print("Vui lòng thêm via vào file via.csv")
    time.sleep(10)
    exit()

max_comments_per_via = 20
num_threads = len(list_via) // 4

post_chunks = [list_link_post[i::num_threads] for i in range(num_threads)]
post_status_chunks = [list_status[i::num_threads] for i in range(num_threads)]
via_chunks = [list_via[i::num_threads] for i in range(num_threads)]
via_status_chunks = [list_status_via[i::num_threads] for i in range(num_threads)]

driver_lock = threading.Lock()
file_lock = threading.Lock()


def get_token(thread_id, two_fa_token):
    time.sleep(uniform(1, 3))
    url = "https://2fa.live/tok/" + two_fa_token
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        token = data["token"]
    else:
        print(f"Lỗi khi lấy mã 2fa ở luồng {thread_id + 1}")
        token = None
    return token


def is_logged_out(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email"]')))
        return True
    except:
        return False


def update_via_status(via, status):
    with file_lock:
        df_list_via = pd.read_csv('via.csv')
        df_list_via["Status"] = df_list_via["Status"].astype(str)
        df_list_via.loc[df_list_via["Via"] == via, "Status"] = status
        df_list_via.to_csv('via.csv', index=False)


def update_post_status(link_post):
    with file_lock:
        df_link_post = pd.read_csv('link_bai_viet.csv')
        df_link_post.loc[df_link_post["Link"] == link_post, "Status"] = 1
        df_link_post.to_csv('link_bai_viet.csv', index=False)


def log_in(driver, thread_id, via, via_status_chunk, via_idx):
    list_via_split = via.split('|')
    account_id, password = list_via_split[0], list_via_split[1]

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email"]'))
        ).click()
    except:
        print(f"Không thể tìm thấy ô nhập tài khoản ở luồng {thread_id + 1}")
        return False

    try:
        ActionChains(driver).send_keys(account_id + Keys.TAB + password + Keys.ENTER).perform()
    except:
        print(f"Không thể nhập tài khoản hoặc mật khẩu ở luồng {thread_id + 1}")
        return False
    time.sleep(uniform(2, 5))
    driver.execute_script("document.body.style.zoom='25%'")

    try:
        found = False
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Email hoặc số di động bạn nhập không kết nối với tài khoản nào')]"))
            )
            found = True
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'The email address or mobile number you entered isn't connected to an account')]"))
                )
                found = True
            except:
                pass
        if found:
            print(f"Tài khoản ở luồng {thread_id + 1} không tồn tại")
            time.sleep(uniform(1, 3))
            update_via_status(via, "Invalid")
            via_status_chunk[via_idx] = "Invalid"
            return False
    except:
        pass

    try:
        found = False
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Mật khẩu bạn nhập không chính xác')]"))
            )
            found = True
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'The password that you've entered is incorrect')]"))
                )
                found = True
            except:
                pass
        if found:
            print(f"Mật khẩu ở luồng {thread_id + 1} không chính xác")
            time.sleep(uniform(1, 3))
            update_via_status(via, "Wrong password")
            via_status_chunk[via_idx] = "Wrong password"
            return False
    except:
        pass

    try:
        found = False
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Kiểm tra thông báo trên thiết bị khác')]"))
            )
            found = True
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Check your notifications on another device')]"))
                )
                found = True
            except:
                pass
        if found:
            if not auto_click(driver, config.try_another_way_button_xpath, 5, 1):
                auto_click(driver, config.try_another_way_button_xpath_eng, 5, 1)
            time.sleep(1)

            try:
                element = driver.find_element(By.XPATH, config.authentication_button_xpath)
            except:
                element = driver.find_element(By.XPATH, config.authentication_button_xpath_eng)
            element.find_element(By.XPATH, config.auth_check_box_xpath).click()
            time.sleep(1)

            if not auto_click(driver, config.continue_button_xpath, 5, 1):
                auto_click(driver, config.continue_button_xpath_eng, 5, 1)
    except:
        pass

    two_fa_token = get_token(thread_id, list_via_split[2])
    time.sleep(3)
    if two_fa_token is None:
        return False

    try:
        ActionChains(driver).send_keys(two_fa_token + Keys.ENTER).perform()
    except:
        print(f"Không thể nhập mã 2fa ở luồng {thread_id + 1}")
    time.sleep(5)

    ActionChains(driver).send_keys(Keys.ESCAPE * 5).perform()

    if "checkpoint" in driver.current_url:
        print(f"Tài khoản ở luồng {thread_id + 1} đã bị checkpoint, đang thực hiện đăng xuất")
        time.sleep(uniform(1, 3))
        update_via_status(via, "Checkpoint")
        via_status_chunk[via_idx] = "Checkpoint"

        try:
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.checkpoint_account_logout_button_xpath))
                ).click()
            except:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.checkpoint_account_logout_button_xpath_eng))
                ).click()
        except:
            print(f"Lỗi khi thực hiện đăng xuất tài khoản checkpoint ở luồng {thread_id + 1}")
            return False

        if not auto_click(driver, config.logout_button_xpath, 5, 1):
            if not auto_click(driver, config.logout_button_xpath_eng, 5, 1):
                print(f"Lỗi khi thực hiện đăng xuất tài khoản checkpoint ở luồng {thread_id + 1}")
                return False
        if not auto_click(driver, config.logout_disable_180d_button_xpath, 5, 1):
            if not auto_click(driver, config.logout_disable_180d_button_xpath_eng, 5, 1):
                print(f"Lỗi khi thực hiện đăng xuất tài khoản checkpoint ở luồng {thread_id + 1}")
                return False
        return False

    if not auto_click(driver, config.trust_device_button_xpath, 5, 1):
        if not auto_click(driver, config.trust_device_button_xpath_eng, 5, 1):
            print(f"Đã tin cậy thiết bị ở luồng {thread_id + 1}")

    return True
# ----------------------------------------------------------------------------------------------------------------------


def main(thread_id, post_chunk, post_status_chunk, via_chunk, via_status_chunk):
    options = uc.ChromeOptions()
    profile_directory = f"Profile_{thread_id + 1}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        try:
            options.user_data_dir = profile_directory
            driver = uc.Chrome(options=options)
        except:
            print(f"Không thể khởi tạo trình duyệt ở luồng {thread_id + 1}, vui lòng update Chrome")
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

    comments_sent = 0

    # -----------------------------------------------------------------------------------------------------------------
    for via_idx, via in enumerate(via_chunk):
        if via_status_chunk[via_idx] != "Active":
            continue

        driver.get("https://www.facebook.com/?locale=vi-VN")
        time.sleep(3)

        print(f"luồng {thread_id + 1} đang chạy tài khoản {via.split('|')[0][-4:]}")
        
        if is_logged_out(driver):
            if not log_in(driver, thread_id, via, via_status_chunk, via_idx):
                continue
        else:
            driver.get("https://www.facebook.com/Phuchuwu/?locale=vi-VN")
            try:
                if not auto_click(driver, config.your_profile_button_xpath, 2, 1):
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, config.checkpoint_account_logout_button_xpath))
                        ).click()
                    except:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, config.checkpoint_account_logout_button_xpath_eng))
                        ).click()
            except:
                print(f"Lỗi khi thực hiện đăng xuất tài khoản ở luồng {thread_id + 1}")
                continue

            if not auto_click(driver, config.logout_button_xpath, 5, 1):
                if not auto_click(driver, config.logout_button_xpath_eng, 5, 1):
                    print(f"Lỗi khi thực hiện đăng xuất tài khoản ở luồng {thread_id + 1}")
                    continue

            if not auto_click(driver, config.logout_disable_180d_button_xpath, 5, 1):
                if not auto_click(driver, config.logout_disable_180d_button_xpath_eng, 5, 1):
                    continue
            continue

        for post_idx, link_post in enumerate(post_chunk):
            if post_status_chunk[post_idx] == 1:
                continue

            if comments_sent >= max_comments_per_via:
                break

            driver.get(link_post + "?locale=vi-VN")
            driver.execute_script("document.body.style.zoom='25%'")
            time.sleep(uniform(5, 15))
            ActionChains(driver).send_keys(Keys.ESCAPE * 5).perform()

            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.comment_button_xpath))
                ).click()
            except:
                print(f"Không thể tìm thấy nút bình luận ở luồng {thread_id + 1}")
                continue
            time.sleep(uniform(2, 5))

            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, config.text_box_xpath))
                )
            except:
                print(f"Không tìm thấy ô nhập bình luận ở luồng {thread_id + 1}")
                update_post_status(link_post)
                post_status_chunk[post_idx] = 1
                continue
            time.sleep(uniform(2, 5))

            try:
                text = choice(list_text)
                ActionChains(driver).send_keys(text + Keys.ENTER).perform()
                time.sleep(2)
                comments_sent += 1
                print(f"Đã bình luận {comments_sent} bình luận bằng tài khoản {via.split('|')[0][-4:]} ở luồng {thread_id + 1}")
            except:
                print(f"Không thể nhập bình luận ở luồng {thread_id + 1}")
                try:
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    continue
                except:
                    print(f"Không thể hủy bình luận ở luồng {thread_id + 1}")
                    continue
            time.sleep(uniform(2, 5))

            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except:
                print(f"Không thể quay lại màn hình khi đã bình luận xong ở luồng {thread_id + 1}")
                continue
            time.sleep(uniform(2, 5))

            update_post_status(link_post)
            post_status_chunk[post_idx] = 1

        comments_sent = 0


threads = []
for idx in range(num_threads):
    thread = threading.Thread(target=main, args=(idx, post_chunks[idx], post_status_chunks[idx], via_chunks[idx], via_status_chunks[idx]))
    thread.start()
    time.sleep(1)
    threads.append(thread)

for thread in threads:
    thread.join()

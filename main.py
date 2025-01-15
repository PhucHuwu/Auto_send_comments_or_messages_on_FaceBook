import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import threading
import os
import pandas as pd
from random import uniform
from click import auto_click


driver_lock = threading.Lock()
confirmation_received = threading.Event()


def main(idx):

    options = uc.ChromeOptions()
    profile_directory = f"Profile_{idx}"
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)

    with driver_lock:
        options.user_data_dir = profile_directory
        try:
            driver = uc.Chrome(options=options)
        except Exception:
            print(f"Lỗi 1 ở luồng {idx + 1}")
            time.sleep(180)
            exit()

    # screen_width = driver.execute_script("return window.screen.availWidth;")
    # screen_height = driver.execute_script("return window.screen.availHeight;")
    # window_width = screen_width // 3
    # window_height = screen_height // 2
    # position_x = idx * window_width // 20
    # position_y = 0

    # driver.set_window_size(window_width, window_height)
    # driver.set_window_position(position_x, position_y)
    driver.maximize_window()

    driver.get("https://www.facebook.com/groups/genshin.vi")
    
    if input() == "ok":
        max_scroll_attempts = 10
        for _ in range(max_scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        posts = driver.find_elements(By.XPATH, '//div[@role="feed"]/div')[1:]

        for idx, post in enumerate(posts, start=1):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                WebDriverWait(post, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Viết bình luận"]'))
                ).click()
                ActionChains(driver).send_keys(f"Bình luận số {idx}").perform()
                print(f"Đã gửi bình luận cho bài viết {idx}.")
                time.sleep(uniform(2, 5))
            except Exception as e:
                print(f"Lỗi khi xử lý bài viết {idx}")

    # confirmation_received.wait()
    # -----------------------------------------------------------------------------------------------------------------


main(1)

# threads = []

# for idx in enumerate(--------------------------------------------------------------------------------------------------?):
#     thread = threading.Thread(target=main, args=(idx))
#     thread.start()
#     threads.append(thread)

# start_program = input("Nhập 'ok' sau khi đã đăng nhập để bắt đầu quá trình spam: ")
# if start_program.lower() == "ok":
#     confirmation_received.set()

# for thread in threads:
#     thread.join()

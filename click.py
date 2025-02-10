from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def auto_click(driver, xpath, time):
    button = WebDriverWait(driver, time).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()

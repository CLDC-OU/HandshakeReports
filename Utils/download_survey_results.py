import logging
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

from utils import config
from utils import initialize_selenium

def download_survey_results(survey_id):
    download_dir = config["user_dir"] + "\\Downloads"
    browser = initialize_selenium()

    # Navigate to the desired website
    website_url = 'https://oakland.joinhandshake.com/edu/surveys/' + survey_id
    browser.get(website_url)

    wait = WebDriverWait(browser, 10)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'sign in with your email address')]")
        )
    )
    login_button.click()
    logging.debug('[Selenium] navigated to login page')

    wait.until(
        EC.element_to_be_clickable(
           (By.XPATH, "//*[contains(text(),'Next')]")
        )
    )

    username_field = browser.find_element(By.ID, 'non-sso-email-address')
    username_field.send_keys(os.getenv('HS_USERNAME'))
    username_field.send_keys(Keys.RETURN)

    continue_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'log in using your Handshake credentials')]")
        )
    )
    continue_button.click()

    password_field = browser.find_element(By.ID, 'password')
    password_field.send_keys(os.getenv('HS_PASSWORD'))

    logging.debug('[Selenium] entered login information')
    password_field.send_keys(Keys.RETURN)

    wait.until(EC.url_contains('edu'))
    logging.debug('[Selenium] logged in')

    #download_button = browser.find_element(By.XPATH, "//*[contains(text(),'Download Results (CSV)')]")
    download_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Download Results (CSV)')]")
        )
    )
    logging.debug('[Selenium] download button loaded')
    download_button.click()
    logging.debug('[Selenium] clicked download button')

    logging.debug('[Selenium] waiting for download to be ready...')
    wait = WebDriverWait(browser, 180)
    download_ready_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Your download is ready. Click here to retrieve the file.')]")
        )
    )

    download_ready_button.click()
    logging.debug('[Selenium] download prepared! downloading...')

    # Wait for the download to finish

    max_wait_time = 30
    initial_files = set(os.listdir(download_dir))

    # Periodically check the downloads directory for new files
    start_time = time.time()
    new_files = False
    while time.time() - start_time < max_wait_time:
        current_files = set(os.listdir(download_dir))

        # Check if there are any new files
        new_files = current_files - initial_files
        if new_files:
            break

        time.sleep(1)  # Wait for 1 second before checking again

    if new_files:
        logging.debug("[Selenium] Successfully downloaded", new_files)
    else:
        logging.error("[Selenium] Download timed out.")

    browser.quit()
import json
import logging
from selenium import webdriver
from dotenv import load_dotenv
import os
from datetime import datetime as dt

with open('config.json') as json_file:
    config = json.load(json_file)


# Load the environmental variables
if load_dotenv():
    logging.debug(f"[Utils {dt.now()}] Environmental variables successfully loaded")
else:
    logging.warn(f"[Utils {dt.now()}] There was an error loading the environmental variables. Check that the path variables are correct and the .env file exists")

def initialize_selenium():
    # Set PATH environmental variable to chromedriver-win64
    os.environ["PATH"] += config['chromedriver_path']

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-minimized")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-popup-blocking")

    # Create a new instance of the Chrome driver
    return webdriver.Chrome(options=chrome_options)

# Returns an array of all months between start and end inclusive
def get_month_range(m:list):
    if len(m) < 2:
        return m
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
            "November", "December"]
    return months[months.index(m[0]):months.index(m[1]) + 1]

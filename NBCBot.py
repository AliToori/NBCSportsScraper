#!usr/bin/env python3
"""
    *******************************************************************************************
    NBCBot: NBC Sports Headlines Scraper
    Author: Ali Toori, Python Developer [Bot Builder]
    Website: https://boteaz.com
    YouTube: https://youtube.com/@AliToori
    *******************************************************************************************

"""
import os
import pickle
import time
import ntplib
import random
import pyfiglet
from datetime import datetime, timedelta
import pandas as pd
import logging.config
from time import sleep
from pathlib import Path
import gspread
from selenium import webdriver
import undetected_chromedriver as uc
from oauth2client.service_account import ServiceAccountCredentials
from multiprocessing import freeze_support
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s] %(log_color)s%(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

LOGGER = logging.getLogger()

# Gmail: morninghuddle11@gmail.com
# Pass: yMpSsp#cy7bHnsY#


class NBCBot:
    def __init__(self):
        self.first_time = True
        self.logged_in = False
        self.driver = None
        self.stopped = False
        self.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        self.PROJECT_ROOT = Path(self.PROJECT_ROOT)
        self.file_path_headlines = str(self.PROJECT_ROOT / "NBCRes/Headlines.csv")
        self.file_path_client_secret = str(self.PROJECT_ROOT / "NBCRes/client-secret_nbcbot.json")
        self.yesterday = str((datetime.now() - timedelta(1)).strftime('%m/%d/%Y'))
        self.today = str((datetime.now() - timedelta(0)).strftime('%m/%d/%Y'))
        self.NBC_HEADLINES_URL = 'https://www.nbcsports.com/edge/football/nfl/player-news/headlines'
        self.NBC_SIGNEDIN_URL = 'https://www.amazon.com/?ref_=nav_signin&'

    def enable_cmd_colors(self):
        # Enables Windows New ANSI Support for Colored Printing on CMD
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Trial version logic
    def trial(self, trial_date):
        ntp_client = ntplib.NTPClient()
        try:
            response = ntp_client.request('pool.ntp.org')
            local_time = time.localtime(response.ref_time)
            current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
            current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            return trial_date > current_date
        except:
            pass

    # Get random user agent
    def get_user_agent(self):
        file_uagents = str(self.PROJECT_ROOT / 'NBCRes/user_agents.txt')
        with open(file_uagents) as f:
            content = f.readlines()
        u_agents_list = [x.strip() for x in content]
        return random.choice(u_agents_list)

    # Get a web driver instance
    def get_driver(self, headless=False):
        LOGGER.info(f"[Launching chrome browser]")
        # For absolute chromedriver path
        DRIVER_BIN = str(self.PROJECT_ROOT / "NBCRes/bin/chromedriver.exe")
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        # prefs = {f"profile.default_content_settings.popups": 0,
        #          f"download.default_directory": f"{self.directory_downloads}",  # IMPORTANT - ENDING SLASH V IMPORTANT
        #          "directory_upgrade": True}
        # options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(F'--user-agent={self.get_user_agent()}')
        if headless:
            options.add_argument('--headless')
        driver = uc.Chrome(executable_path=DRIVER_BIN, options=options)
        return driver

    def finish(self):
        LOGGER.info("[Closing the browser instance]")
        try:
            if not self.stopped:
                self.driver.close()
                self.driver.quit()
                self.stopped = True
        except WebDriverException as exc:
            LOGGER.info(f'[Problem occurred while closing the browser instance: {exc.args}]')

    def get_headlines(self, start_date, end_date):
        LOGGER.info(f'[Retrieving headlines for: {start_date} - {end_date}]')
        months = {"Jan": '1', "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6",
                  "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"}
        by_child_item = 'ByChildItem'
        # Get browser
        if self.driver is None:
            self.driver = self.get_driver()
        LOGGER.info(f'[Navigating to headlines]')
        self.driver.get(url=self.NBC_HEADLINES_URL)
        # LOGGER.info(f'[Filtering headlines]')
        try:
            self.wait_until_visible(driver=self.driver, class_name='player-news-article__body')
        except:
            self.wait_until_visible(driver=self.driver, css_selector='.player-news-article__body')
        LOGGER.info(f'[Headlines are being retrieved: {start_date}]')
        for post in self.driver.find_elements_by_css_selector('.player-news-article__body'):
            post_date = str(self.driver.find_element_by_class_name('player-news-article__timestamp').text)[:13].replace(',', '')
            # Replace Month abbreviation with its respective digit
            post_date = [post_date.replace(m, d) for m, d in months.items() if m in post_date]
            LOGGER.info(f'Post Date: {post_date[0]}')
            post_date = datetime.strptime(post_date[0].strip(), '%m %d %Y').strftime('%m/%d/%Y')
            post_date = datetime.strptime(post_date, '%m/%d/%Y')
            # If post is from today or Yesterday
            if post_date >= start_date:
                post_date = post_date.strftime('%m/%d/%Y')
                post_headline = str(post.find_element_by_tag_name('h3').text).replace(',', '')
                LOGGER.info(f"[Post Headline: {post_headline}]")
                post_description = str(post.find_element_by_tag_name('p').text).replace(',', '')
                LOGGER.info(f"[Post Description: {post_headline}]")
                post_source = post.find_element_by_tag_name('a').get_attribute('href')
                LOGGER.info(f"[Post Scource: {post_headline}]")
                df_dict = {'PostDate': [post_date], 'Headline': [post_headline], 'Description': [post_description], 'Source': [post_source],}
                df = pd.DataFrame(df_dict)
                df.to_csv(self.file_path_headlines, index=False)
                # if file does not exist write header
                # if not os.path.isfile(self.file_path_headlines) or os.path.getsize(self.file_path_headlines) == 0:
                #     df.to_csv(self.file_path_headlines, index=False)
                # else:  # else if exists so append without writing the header
                #     df.to_csv(self.file_path_headlines, mode='a', header=False, index=False)

    def csv_to_spreadsheet(self, csv_path, sheet_url, sheet_name):
        LOGGER.info(f"[Updating headlines in the Google Sheet: {sheet_name}]")
        df = pd.read_csv(csv_path, index_col=None)
        sheet_key = '1b25493dd39d82f2712c0c33fefeed1bb0d45415'
        client_email = ''
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.file_path_client_secret, scope)
        client = gspread.authorize(credentials)
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        LOGGER.info(f"[Updates have been made to the Google Sheet: Name: {sheet_name}, URL: {sheet_url}]")

    def wait_until_clickable(self, driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None,
                             css_selector=None, duration=10000, frequency=0.01):
        if xpath:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
        elif css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

    def wait_until_visible(self, driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None,
                           css_selector=None, duration=10000, frequency=0.01):
        if xpath:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
        elif css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    def main(self):
        # freeze_support()
        # self.enable_cmd_colors()
        trial_date = datetime.strptime('2021-06-20 23:59:59', '%Y-%m-%d %H:%M:%S')
        # Print ASCII Art
        print('************************************************************************\n')
        pyfiglet.print_figlet('____________                   NBCBot ____________\n', colors='RED')
        print('Author: Ali Toori, Bot Developer\n'
              'Website: https://boteaz.com/\n************************************************************************')
        # Trial version logic
        if self.trial(trial_date):
            # LOGGER.warning("[Your trial will end on: ",
            #       str(trial_date) + ". To get full version, please contact fiverr.com/botflocks !]")
            file_path_account = str(self.PROJECT_ROOT / "NBCRes/Accounts.csv")
            if os.path.isfile(file_path_account):
                account_df = pd.read_csv(file_path_account, index_col=None)
                # num_workers = len(account_df)
                while True:
                    # Get accounts from Accounts.csv
                    for account in account_df.iloc:
                        start_date = int(account["StartDate"])
                        end_date = int(account["EndDate"])
                        sheet_url = account["SheetURL"]
                        sheet_name = account["SheetName"]
                        # Convert date_string to datetime object
                        yesterday = datetime.strptime(self.yesterday, '%m/%d/%Y')
                        today = datetime.strptime(self.today, '%m/%d/%Y')
                        self.get_headlines(start_date=yesterday, end_date=today)
                        self.csv_to_spreadsheet(csv_path=self.file_path_headlines, sheet_url=sheet_url, sheet_name=sheet_name)
                    self.finish()
                    LOGGER.info(f"Process completed successfully")
                    LOGGER.info(f"The process will auto-restart after 24 hours")
                    sleep(86400)
        else:
            pass
            # LOGGER.warning("Your trial has been expired")
            # LOGGER.warning("Please contact https://botflocks.com")


if __name__ == '__main__':
    NBC_bot = NBCBot()
    NBC_bot.main()

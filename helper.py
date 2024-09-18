#!/usr/bin/python3
__author__ = 'agoss'

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime


def yahoo_account_login(user_email, user_pw, browser):
    """
    Login to Yahoo account to access fantasy football player projections based on league settings.
    """

    browser.get('https://login.yahoo.com')
    email_elem = browser.find_element(By.ID, 'login-username')
    email_elem.send_keys(user_email)
    login_btn = browser.find_element(By.ID, 'login-signin')
    login_btn.click()
    pw_elem = WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_element_located((By.ID, 'login-passwd'))
    )
    pw_elem.send_keys(user_pw)
    submit_btn = browser.find_element(By.ID, 'login-signin')
    submit_btn.click()
    return browser

def get_next_nfl_week(current_week: int) -> int:
    return current_week + 1

def get_current_nfl_week(start_date: datetime, current_date: datetime) -> int:
    days_since_start = (current_date - start_date).days
    return days_since_start // 7 + 1
from datetime import datetime
import os

from selenium.webdriver.support.wait import WebDriverWait

from bot_driver import marionette_driver, login_linkedin_withwebdriver, \
    IDLE_INTERVAL_IN_SECONDS
from bot_mysql import exist_user
from bot_mysql2 import check_password_correct, pinverify
from captcha_solver import check_captcha

import bottask_status as botstatus
from time import sleep


def login_linkedinx(email, password, driver=None, pincode=None,
    cur=None, owner_id=None, task_id=None, task_type=None):
    print("==== LOGIN =====")
    lastrun_date = datetime.now()
    completed_date = datetime.now()
    
    login_linkedin_withwebdriver(email, password, driver)
    print('get login_linkedin_withwebdriver driver')

    wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
    # check if user is exist
    bot_status = botstatus.DONE
    if exist_user(wait):
        print("That user is an existing user.")
        
        if check_password_correct(wait):
            print('pw is correct')
            sleep(1000)
            res = check_captcha(driver)
            
    
                
    
    


user_email = os.environ.get('email', None)
user_pw = os.environ.get('pw', None)

browser = marionette_driver(proxy_ip='127.0.0.1', proxy_port=8080, 
                            headless=False)

login_linkedinx(user_email,user_pw, browser)

sleep(IDLE_INTERVAL_IN_SECONDS)
browser.close()

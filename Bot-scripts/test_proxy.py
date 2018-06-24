from datetime import datetime
import json
import os
from time import sleep
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from bot import exist_user, check_password_correct
from bot_driver import marionette_driver, login_linkedin_withwebdriver, \
    IDLE_INTERVAL_IN_SECONDS, get_driver, SEARCH_URL, get_browser_csrf_tocken, \
    LINKEDIN_URL
import bottask_status as botstatus
from captcha_solver import check_captcha
from _datetime import date


user_email = os.environ.get('email', None)
user_pw = os.environ.get('pw', None)


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
        
            res = check_captcha(driver)
            
def search():
    driver = get_driver(user_email, user_pw, force_login=True
                        )
    if 'feed' not in driver.current_url:
        driver.get(SEARCH_URL)

    print("==== SEARCH ======")
    limit = 100
    
    search_mode = 0
    search_data = 'do less earn more'
    
    try:
        if search_mode == 0:
            time.sleep(5)
            # search connection
            search_input = driver.find_element_by_xpath(
                "/html/body/nav/div/form/div/div/div/artdeco-typeahead-deprecated/artdeco-typeahead-deprecated-input/input")
            keyword = search_data
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)

            print("-------click search button-----------")

            time.sleep(5)
            total_resultcounts_tag = driver.find_element_by_css_selector(
                "h3.search-results__total")
            total_resultcounts = total_resultcounts_tag.text
            result_counts = total_resultcounts.split(" ")
            real_counts = result_counts[1]
            counts = real_counts.replace(",", "")
            print('counts:', counts)
            range_count = int(counts) // 10 + 1
            print('range_count:', range_count)
            range_count = 10

            parse_urls = {}
            print('parsing url:')
            count = 0
            for _ in range(range_count):
                time.sleep(3)
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(3)

                search_list = driver.find_elements_by_class_name(
                    "search-result__result-link")
                #print('search_list:', search_list)
                

                #for search_index in range(len(actor_name_lists)):

                for tag in search_list:
                    url = tag.get_attribute('href')
                    if url in parse_urls or 'result' in url:
                        continue
                    parse_urls[url] = 1
                    count += 1
                    if count >= limit:
                        break
                    
                if count >= limit:
                        break

                try:
                    driver.find_element_by_class_name("next").click()
                except Exception as err1:
                    print('No next:', err1)
                    break
            
            get_search_contact(parse_urls, driver)
        
    except Exception as err:
        print('execption:', err)
        
    driver.close()
 

    
def get_search_contact(parse_urls, driver):
    print('parsing profile:')
    csrf_tocken = get_browser_csrf_tocken(driver)
    for count, url in enumerate(parse_urls.keys()):
        try:
            uid = url.split('/')[-2]
            contact = get_contact_ajax(driver, uid, csrf_tocken)
            print('count:', count + 1,  contact)
        except:
            continue
        
    
def test_suff():
    
    browser = marionette_driver(proxy_ip='127.0.0.1', proxy_port=8080, 
                                headless=False)
    
    login_linkedinx(user_email,user_pw, browser)
    
    sleep(IDLE_INTERVAL_IN_SECONDS)
    browser.close()
    
    
if __name__ == '__main__':
    start = time.time()
    search()
    done = time.time() - start
    
    print('done in:', done, ' secs')

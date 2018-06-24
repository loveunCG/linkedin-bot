"""
# this solves captcha of linkedin & returns captcha response
"""
import datetime
import sys
import time
import traceback

from python_anticaptcha import NoCaptchaTaskProxylessTask, AnticaptchaClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bot_db import get_cursor
from bot_email import send_email
from bot_sql import bottask_update_query
import bottask_status
from freebotIP import get_ip


#  from bot_mysql2 import bottask_update_query
IDLE_INTERVAL_IN_SECONDS = 5

# 
API_KEY = '91e6b240571c9b718be9095125ca51a0'

#site_key = '6LfTDSgTAAAAAMgNPKDdkNqxq81KTDWrL7gOabTt' # grab from site
SITE_KEY = '6Lc7CQMTAAAAAIL84V_tPRYEWZtljsJQJZ5jSijw' #linkedin
            
def solve_captcha(url):
    print("solving captcha....")
    res = None
    try:

        client = AnticaptchaClient(API_KEY)
        task = NoCaptchaTaskProxylessTask(url, SITE_KEY)
        job = client.createTask(task)
        job.join()
        res = job.get_solution_response()
        print("Captcha solved !!")
        
    except Exception as err:
        print("Captcha not solved... Error:", err)
        
      
    return res

def check_captcha(browser, task_id, task_type, owner_id,
                  email, password):
    
    cur = get_cursor()
    lastrun_date = datetime.datetime.now()
    
    completed_date = lastrun_date
    update_status = bottask_status.CAPTCHA_SOLVING
    
    done = False
    while done == False:
            
        try:
            selector = browser.find_element_by_css_selector("#noCaptchaIframe")
            # when this is ready on ui, use this
            # cur.execute(bottask_update_query, (update_status, lastrun_date,
            #                           completed_date, task_id, task_type, owner_id))
            
            send_email(email, password, get_ip())
            
            time.sleep(IDLE_INTERVAL_IN_SECONDS)
            
        except Exception as err:
            print('noCaptchaIframe:', err)
            done = True
    
    return True

def check_captcha_xx(browser):
    
    recaptcha_elem = None
    
    url = None
    # it not done yet
    #return True

    done = False
    try:
        selector = browser.find_element_by_css_selector("#noCaptchaIframe")
        
    except Exception as err:
        print('noCaptchaIframe:', err)
        return True
    
    try:
        exc_info = sys.exc_info()
        
        selector = browser.find_element_by_css_selector("#noCaptchaIframe")
        browser.switch_to.frame(selector)
        
        #, "#nocaptcha > div > div > iframe")
        frame2css = "#nocaptcha > div > div > iframe"
        iframe2 = browser.find_element_by_css_selector(frame2css)
        
        
        url = iframe2.get_attribute('src')
        print('captchar url:',  url)
        
        
        recaptcha_elem = browser.find_element_by_id('g-recaptcha-response')
        script = """document.getElementById('g-recaptcha-response').style.height='50px';
         document.getElementById('g-recaptcha-response').style.display='block';"""
        browser.execute_script(script, recaptcha_elem)
        recaptcha_elem.clear()
        
        print("Processing re-captcha...")
        ## Captcha processed
        res = solve_captcha(url)
        #res= "safasfasdfasfasdfasdfasdfasdfadsfasdfasdfasdfasdfsadfasdffffff"
        
        if res:
            # recaptcha_elem.send_keys(res)
            script= """document.getElementById('g-recaptcha-response').innerHTML="{0}";""".format(res)
            browser.execute_script(script)
            time.sleep(IDLE_INTERVAL_IN_SECONDS)
            
            script= """grecaptchaData.sitekey='{0}';
            completedCaptcha();
            """.format(SITE_KEY)
            
            print("solved...", script)
            browser.execute_script(script)
            
            time.sleep(5)
            
            done = True
            
            if done == False:
            
                browser.switch_to.default_content()
                
                
                
                nocaptcha_id = 'nocaptcha-response'
                nocaptca =browser.find_element_by_id(nocaptcha_id)
                x = nocaptca.location.get('x', 0)
                y = nocaptca.location.get('y', 1000)
                script = "window.scrollBy({x},{y});".format(x=x,y=y)
                print('script:', script)
                browser.execute_script(script)
                script= 'document.getElementById("{nocaptcha_id}").value = "{val}"'.format(
                    val=res, nocaptcha_id=nocaptcha_id)
                print('script:', script)
                browser.execute_script(script,nocaptca)
                
                # find the captcha form and sumbit
                challenge_form_id = '#challengeContent > form'
                challenge_form=browser.find_element_by_css_selector(challenge_form_id)
                script= """document.getElementsByClassName('{button_id}')[0].style.height='200px';
                 document.getElementsByClassName('{button_id}')[0].style.display='block';""".format(button_id='cp-challenge-form')
                browser.execute_script(script,challenge_form)
                print('script:', script)
                browser.execute_script("window.scrollBy({x},{y});".format(x=challenge_form.location.get('x', 0), 
                                                                          y=challenge_form.location.get('y', 1000)))
                challenge_form.click()
                time.sleep(50)
                
                # continue button
                submit_button_id = 'btn-fallback-submit'
                coninue_button=browser.find_element_by_id(submit_button_id)
                script= """document.getElementById('{button_id}').style.height='50px';
                 document.getElementById('{button_id}').style.display='block';""".format(button_id=submit_button_id)
                browser.execute_script(script,coninue_button)
                print('script:', script)
                browser.execute_script("window.scrollBy({x},{y});".format(x=coninue_button.location.get('x', 0), 
                                                                          y=coninue_button.location.get('y', 1000)))
                print('scroll to button:', submit_button_id)
                time.sleep(3)
                #coninue_button = browser.find_element_by_id(submit_button_id)
                coninue_button.click()
                time.sleep(IDLE_INTERVAL_IN_SECONDS)
                done = True
        else:
            browser.switch_to.default_content()

    except Exception as err:
        print('g-recaptcha error:', err)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)

    finally:
        traceback.print_exception(*exc_info)
        del exc_info
         
    return done
    
        
    

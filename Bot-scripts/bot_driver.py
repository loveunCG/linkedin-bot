import os
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


LINKEDIN_URL = "https://www.linkedin.com"
SEARCH_URL = "%s/feed/" % LINKEDIN_URL
LINKEDIN_CONNECTIONS_URL = "{0}/mynetwork/invite-connect/connections/".format(LINKEDIN_URL)

IDLE_INTERVAL_IN_SECONDS = 5


FF_DRIVER = None


def marionette_driver(**kwargs):
    proxy_port = kwargs.get('proxy_port', None)
    proxy_ip = kwargs.get('proxy_ip', None)

    options = Options()
    if kwargs.get('headless', True):
        options.add_argument('--headless')

    dir_ = os.path.dirname(__file__)
    ffProfilePath = os.path.join(dir_, "FirefoxSeleniumProfile")
    if os.path.isdir(ffProfilePath) == False:
        os.mkdir(ffProfilePath)

    profile = webdriver.FirefoxProfile(profile_directory=ffProfilePath)

    # profile = webdriver.FirefoxProfile()
    if proxy_ip and proxy_port:
        print('setting proxy')
        profile.set_preference('network.proxy.socks_port', int(proxy_port))
        profile.set_preference('network.proxy.socks', proxy_ip)
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy_ip)
        profile.set_preference("network.proxy.http_port", int(proxy_port))
        profile.update_preferences()

    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    #firefox_capabilities['binary'] = '/usr/bin/firefox'
    #driver = webdriver.Firefox(capabilities=firefox_capabilities)
    firefox_capabilities['handleAlerts'] = True
    firefox_capabilities['acceptSslCerts'] = True
    firefox_capabilities['acceptInsecureCerts'] = True
    firefox_capabilities['javascriptEnabled'] = True

    # cap = {'platform': 'ANY', 'browserName': 'firefox', 'version': '', 'marionette': True, 'javascriptEnabled': True}
    driver = webdriver.Firefox(options=options, firefox_profile=profile,
                               capabilities=firefox_capabilities)

    #driver = webdriver.Firefox(options=options,
    #                        capabilities=firefox_capabilities)
    if 'loadsession' in kwargs:
        load_session(driver, kwargs.get('email'))

    return driver

def get_sesssion_file(email):
    dir_ = os.path.dirname(__file__)
    LINKEDIN_COOKIE_FILE = os.path.join(dir_, "LinkedinCookies")
    if os.path.isdir(LINKEDIN_COOKIE_FILE) == False:
        os.makedirs(LINKEDIN_COOKIE_FILE)
    
    return os.path.join(LINKEDIN_COOKIE_FILE, email)


def store_session(driver, email='1'):
    storefile = get_sesssion_file(email)
    print('storing cookie:', storefile)    
    pickle.dump(driver.get_cookies() , open(storefile,"wb"))
    
def load_session(driver, email="1"):
    storefile = get_sesssion_file(email)
    print('reading cookie:', storefile)
    driver.get(LINKEDIN_URL)
    try:
            
        for cookie in pickle.load(open(storefile, "rb")):
            driver.add_cookie(cookie)
    except Exception as err:
        print('error:', err)
    
    
def login_linkedin_withwebdriver(email, password, driver=None):
    user_email = email
    user_password = password
    
    # driver = botdriver.ff_driver()
    if driver is None:
        # , proxy_ip='127.0.0.1', proxy_port=8080,
        # driver = marionette_driver(headless=False)
        # driver = marionette_driver(proxy_ip='127.0.0.1', proxy_port=8080,
        #                           headless=False)
        # head less
        # driver = marionette_driver()
        driver = marionette_driver(headless=False)

    driver.get(LINKEDIN_URL)
    wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)

    print("----working-----")
    email = get_email_input(wait)


    password = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input#login-password")))
    print("------pass password---------")

    signin_button = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input#login-submit")))
    print("------pass button---------")

    email.clear()
    password.clear()

    email.send_keys(user_email)
    password.send_keys(user_password)

    signin_button.click()
    print("----------click sign in----------------")

    return driver


def get_email_input(wait):
    email = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input#login-email")))
    print("------pass email---------")
    return email


def get_driver(email, password, **kwargs):
    
    driver = marionette_driver(headless=False, loadsession=True,
                               email=email)
    
    
    # only if it is not login
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        email_ele = get_email_input(wait)
        
        print('Login already. Do nothing more:', email_ele)
        driver = login_linkedin_withwebdriver(email, password, driver)
        
    except Exception as err:
        print('email is not there:', err)
        
            
    return driver

def close_driver(driver, email):
    store_session(driver, email)
    driver.close()
    
def get_browser_csrf_tocken(driver):
        
    # request_cookies_browser = driver.get_cookies()
    JSESSIONID = driver.get_cookie('JSESSIONID')
    csrf_tocken = JSESSIONID['value']
    return csrf_tocken

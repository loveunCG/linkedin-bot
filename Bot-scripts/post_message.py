
from datetime import date, datetime
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bot_db import get_cursor, get_db, get_user_email_pw
from bot_driver import login_linkedin_withwebdriver, LINKEDIN_URL, \
    IDLE_INTERVAL_IN_SECONDS, get_driver
import bot_msgtype
import bottask_status
import bottask_type


message_select = """select * from messenger_chatmessage where id = %s"""
contact_select = """select * from messenger_inbox where id = %s"""
message_update_sql = """update messenger_chatmessage set is_sent=1 where id = %s"""
bottask_update_status_sql = "UPDATE app_bottask SET status=%s WHERE id=%s "
bottask_update_done_sql = "UPDATE app_bottask SET status=(%s), lastrun_date=(%s), completed_date=(%s) WHERE id=%s "

message_update_reply_sql = """update messenger_chatmessage set replied_date=%s where id = %s"""

message_time_update_sql = """update messenger_chatmessage set time=%s where id = %s"""

messages_replied_insert_query = """INSERT INTO messenger_chatmessage (created_at, update_at, text, time, type, contact_id,
replied_date, campaign_id, owner_id, campaignstep_id, is_direct, is_read, is_sent)
 VALUES (%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)"""

contact_update_status_connect_sql = """update messenger_inbox set status=12 where id = %s"""


def update_message_is_sent(cur, message_id):
    cur.execute(message_update_sql, (message_id))


def update_message_replied(cur, replied_date, msg, msgdetail):
    try:
        cur.execute(message_update_reply_sql, (replied_date, msgdetail[0]))
        # insert the replied mssage
        now = datetime.now()
        new_value = (now, now, msg, replied_date, bot_msgtype.TALKING_REPLIED_N, msgdetail[6],
                     replied_date, msgdetail[9], msgdetail[10], msgdetail[0],
                     0, 0, 0)
        print('msgdetail:', msgdetail)
        print(messages_replied_insert_query % new_value)
        cur.execute(messages_replied_insert_query, new_value)
        cur.execute(contact_update_status_connect_sql, (msgdetail[0]))
    except Exception as e:
        print('------->', e)


def handle_postmessage_pre(cur, taskrow):
    msgdetail = get_db(cur, message_select, (taskrow[8],))
    print('message detail:', msgdetail)
    # update runniing status
    cur.execute(bottask_update_status_sql,
                (bottask_status.RUNNING, taskrow[0]))
    return msgdetail


def handle_postmessage(cur, taskrow):
    msgdetail = handle_postmessage_pre(cur, taskrow)
    # do_post with webdriver
    res = postmessage_browser(cur, taskrow, msgdetail)
    # update message
    task_status = bottask_status.ERROR
    if res:
        task_status = bottask_status.DONE
        update_message_is_sent(cur, msgdetail[0])
    handle_postmessage_post(cur, task_status, taskrow[0])


def handle_postmessage_post(cur, task_status, task_id):
    now = datetime.now()
    cur.execute(bottask_update_done_sql, (task_status, now, now, task_id))


def handle_checkmessage(cur, taskrow):
    msgdetail = handle_postmessage_pre(cur, taskrow)
    print('msgdetail:', msgdetail)
    # do_post with webdriver
    res, replied_date, msg = checkmessage_browser(cur, taskrow, msgdetail)
    # update message
    print('check_message result------->', res, replied_date, msg)
    task_status = bottask_status.ERROR
    if res and replied_date is not None:
        task_status = bottask_status.DONE
        update_message_replied(cur, replied_date, msg, msgdetail)
    if res is not None:
        task_status = bottask_status.DONE
    handle_postmessage_post(cur, task_status, taskrow[0])


def checkmessage_browser(cur, taskrow, msgdetail):
    email, password = get_user_email_pw(cur, taskrow[6])
    try:
        contact = get_db(cur, contact_select, (msgdetail[6], ))
    except Exception as e:
        print('----->', e)
        return
    print('contact:', contact)
    # driver = login_linkedin_withwebdriver(email, password)
    driver = get_driver(email, password)
    user_path = "/in/{0}/".format(contact[10])
    # go to the user homme
    userhome = "{0}{1}".format(LINKEDIN_URL, user_path)
    print('userhome:', userhome)
    status = True
    replied_date = None
    message = ""
    # click on the send message
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        driver.get(userhome)
        # pv-s-profile-actions--message
        #message_btn = driver.find_element_by_class_name("pv-s-profile-actions--message")
        message_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button.pv-s-profile-actions--message")))
        message_btn.click()
        # post the text in the right box
        box_css = """div.application-outlet>aside.msg-overlay-container div.msg-overlay-conversation-bubble div.msg-overlay-conversation-bubble__content-wrapper div.msg-s-message-list-container """
        #  textarea.ember-text-area msg-form__textarea"
        msg_box = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, box_css)))
        script = "window.scrollBy({x},{y});".format(x=msg_box.location.get('x', 0),
                                                    y=msg_box.location.get('y', 1000))
        print('script:', script)
        driver.execute_script(script)
        # print('get_attribute:', msg_box.get_attribute('innerHTML'))
        msg_list_css = "{0} {1}".format(box_css, "ul.msg-s-message-list>li")
        print('msg_list_css:', msg_list_css)
        message_list = driver.find_elements_by_css_selector(msg_list_css)
        html = message_list[-1].get_attribute('innerHTML')
        if user_path in html:
            # found replied
            replied_date = datetime.now()
            m = re.search(r'([\d]+):([\d]+)\s+([AP]M)', html)
            print('time:', m)

            if m:
                hr = int(m.group(1))
                mi = int(m.group(2))
                if m.group(3) == "PM":
                    hr += 12
                d = replied_date.day
                if hr < replied_date.hour:
                    d = d - 1

                replied_date = replied_date.replace(minute=mi, hour=hr,
                                                    day=d)
                print('replied_date:', replied_date)
            # get message
            try:
                m = message_list[-1].find_element_by_css_selector('p.msg-s-event-listitem__body').text
            except Exception as e:
                print('error ----->', e)
                pass
            if m:
                message = m.strip()
                print('message:', message)
    except Exception as err:
        print('send message error:', err)
        status = False
    # check back id?
    driver.close()
    return status, replied_date, message


def postmessage_browser(cur, taskrow, msgdetail):
    email, password = get_user_email_pw(cur, taskrow[6])
    contact = get_db(cur, contact_select, (msgdetail[6], ))
    print('contact:', contact)
    # driver = login_linkedin_withwebdriver(email, password)
    driver = get_driver(email, password)
    # go to the user homme
    userhome = "{0}/in/{1}/".format(LINKEDIN_URL, contact[10])
    print('userhome:', userhome)
    status = True
    # click on the send message
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        driver.get(userhome)
        # pv-s-profile-actions--message
        #message_btn = driver.find_element_by_class_name("pv-s-profile-actions--message")
        message_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button.pv-s-profile-actions--message")))
        message_btn.click()
        # post the text in the right box
        box_css = """div.application-outlet>aside.msg-overlay-container div.msg-overlay-conversation-bubble div.msg-overlay-conversation-bubble__content-wrapper form.msg-form """
        #  textarea.ember-text-area msg-form__textarea"
        form_box = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, box_css)))
        script = "window.scrollBy({x},{y});".format(x=form_box.location.get('x', 0),
                                                    y=form_box.location.get('y', 1000))
        print('script:', script)
        driver.execute_script(script)
        #print('get_attribute:', form_box.get_attribute('innerHTML'))
        text_box_css = "{0} {1}".format(
            box_css, "div.msg-form__compose-area>textarea[name='message']")
        print('text_box_css:', text_box_css)
        message_box = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, text_box_css)))
        message_box.send_keys(msgdetail[3])
        message_box.send_keys(Keys.RETURN)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)
        # send
        button_css = "{0} {1}".format(
            box_css, "footer button.msg-form__send-button")
        try:
            send_btn = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, button_css)))
            send_btn.click()
        except Exception as e:
            print('------->', e)
        print('---->click end message<------')
        message_time = get_send_message_date(driver)
        if message_time is not None:
            try:
                cur.execute(message_time_update_sql, (message_time, msgdetail[0]))
            except Exception as e:
                print('----->', e)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)
    except Exception as err:
        print('send message error:', err)
        status = False
    # check back id?
    driver.close()
    return status


def get_send_message_date(driver):
    message_time = datetime.now()
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        box_css = """div.application-outlet>aside.msg-overlay-container div.msg-overlay-conversation-bubble div.msg-overlay-conversation-bubble__content-wrapper div.msg-s-message-list-container """
        msg_box = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, box_css)))
        script = "window.scrollBy({x},{y});".format(x=msg_box.location.get('x', 0),
                                                    y=msg_box.location.get('y', 1000))
        driver.execute_script(script)
        msg_list_css = "{0} {1}".format(box_css, "ul.msg-s-message-list>li")
        message_list = driver.find_elements_by_css_selector(msg_list_css)
        html = message_list[-1].get_attribute('innerHTML')
        m = re.search(r'([\d]+):([\d]+)\s+([AP]M)', html)
        print('time:', m)
        if m:
            hr = int(m.group(1))
            mi = int(m.group(2))
            if m.group(3) == "PM":
                hr += 12
            d = message_time.day
            if hr < message_time.hour:
                d = d - 1
                message_time = message_time.replace(minute=mi, hour=hr, day=d)
            print('replied_date:', message_time)
    except Exception as err:
        print('send message error:', err)
    return message_time


def test_handle_message():
    cur = get_cursor()
    cur.execute("SELECT * FROM app_bottask where status ='%s' or status='%s' order by id desc limit 1" % (bottask_status.QUEUED,
                                                                                                          bottask_status.PIN_CHECKING))
    row = cur.fetchone()
    print('row:', row)
    if row is not None and row[1] == bottask_type.POSTMESSAGE:
        handle_checkmessage(cur, row)


if __name__ == "__main__":
    test_handle_message()

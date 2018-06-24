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

message_update_reply_sql = """update messenger_chatmessage set replied_other_date=%s where id = %s"""
message_update_reply_ignore_sql = """update messenger_chatmessage set replied_date=%s where id = %s"""
contact_update_connect_sql = """update messenger_inbox set is_connected=1, connected_date=%s where id = %s"""
delete_search_result_sql = """DELETE FROM connector_searchresult WHERE linkedin_id=%s"""

messages_replied_insert_query = """INSERT INTO messenger_chatmessage (created_at, update_at, text, time, type, contact_id,
replied_date, campaign_id, owner_id, campaignstep_id, is_direct, is_read, is_sent)
 VALUES (%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)"""

contact_update_status_connect_sql = """update messenger_inbox set status=12 where id = %s"""


def update_message_is_sent(cur, message_id):
    cur.execute(message_update_sql, (message_id))


def update_message_replied(cur, replied_date, msg, msgdetail):
    cur.execute(message_update_reply_sql, (replied_date, msgdetail[0]))
    print('-------update_message_replied--- ------')


def update_message_replied_ignore(cur, replied_date, msg, msgdetail):
    cur.execute(message_update_reply_ignore_sql, (replied_date, msgdetail[0]))
    print('-------update_message_replied--- -->------')


def update_contact_connected(cur, connected_date, msgdetail, message=None):
    cur.execute(contact_update_connect_sql, (connected_date, msgdetail[6]))
    contact = get_db(cur, contact_select, (msgdetail[6],))
    cur.execute(delete_search_result_sql, (contact[10]))
    if message is not None:
        print('-------delete---search result------', contact[10])
        now = datetime.now()
        new_value = (now, now, message, replied_date, bot_msgtype.TALKING_REPLIED_N, msgdetail[6],
                     replied_date, msgdetail[9], msgdetail[10], msgdetail[0],
                     0, 0, 0)
        print('msgdetail:', msgdetail)
        print(messages_replied_insert_query % new_value)
        cur.execute(messages_replied_insert_query, new_value)
        cur.execute(contact_update_status_connect_sql, (msgdetail[6]))
        print('connect is connected!')


def handle_postconnect_pre(cur, taskrow):
    print('taskrow:', taskrow)
    msgdetail = get_db(cur, message_select, (taskrow[8],))
    print('message detail:', msgdetail)
    # update runniing status
    cur.execute(bottask_update_status_sql, (bottask_status.RUNNING, taskrow[0]))
    return msgdetail


def handle_postconnect(cur, taskrow):
    msgdetail = handle_postconnect_pre(cur, taskrow)
    # do_post with webdriver
    res = postconnect_browser(cur, taskrow, msgdetail)
    # update message
    task_status = bottask_status.ERROR
    if res:
        task_status = bottask_status.DONE
        update_message_is_sent(cur, msgdetail[0])

    handle_postconnect_post(cur, task_status, taskrow[0])


def handle_postconnect_post(cur, task_status, task_id):
    # update bottask

    now = datetime.now()
    cur.execute(bottask_update_done_sql, (task_status, now, now, task_id))


def handle_checkconnect(cur, taskrow):
    msgdetail = handle_postconnect_pre(cur, taskrow)
    print('msgdetail:', msgdetail)
    # do_post with webdriver
    res, replied_date, connect, msg = checkconnect_browser(cur, taskrow, msgdetail)

    task_status = bottask_status.DONE
    # update connected when connect
    if connect == "connected":
        update_contact_connected(cur, replied_date, msgdetail, msg)

    # update replied_other_date
    if connect == "ignored":
        update_message_replied(cur, replied_date, connect, msgdetail)

        if msg is not None:
            update_message_replied_ignore(cur, replied_date, connect, msgdetail)

    handle_postconnect_post(cur, task_status, taskrow[0])


def checkconnect_browser(cur, taskrow, msgdetail):
    email, password = get_user_email_pw(cur, taskrow[6])
    contact = get_db(cur, contact_select, (msgdetail[6],))
    print('contact:', contact)
    # driver = login_linkedin_withwebdriver(email, password)
    driver = get_driver(email, password)
    user_path = "/in/{0}/".format(contact[10])
    # go to the user homme
    userhome = "{0}{1}".format(LINKEDIN_URL, user_path)
    print('userhome:', userhome)
    status = True
    replied_date = datetime.now()
    connect = ""
    message = None
    # click on the send connect
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        driver.get(userhome)
        message_btn = None
        pending_btn = None
        inmail_btn = None
        try:
            pending_btn = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "button.pv-s-profile-actions--pending")))
        except Exception as e:
            print('---no pending---', e)
            try:
                inmail_btn = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "button.pv-s-profile-actions--send-in-mail")))
            except Exception as e:
                print('---no ignored---', e)
                try:
                    message_btn = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "button.pv-s-profile-actions--message")))
                except Exception as e:
                    print('---no connected---', e)

        if inmail_btn is not None:
            connect = "ignored"

        if pending_btn is not None:
            connect = "pending"

        if message_btn is not None or inmail_btn is not None:
            if message_btn is not None:
                connect = "connected"
                find_contact_on_message_box(driver, contact)
                # open_msg_box_btn = "button.msg-overlay-bubble-header__control--new-convo-btn"
                # open_msg_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, open_msg_box_btn)))
                # message_btn.click()
            if inmail_btn is not None:
                find_contact_on_message_box(driver, contact)
            box_css = """div.application-outlet>aside.msg-overlay-container div.msg-overlay-conversation-bubble div.msg-overlay-conversation-bubble__content-wrapper div.msg-s-message-list-container"""
            try:
                msg_box = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, box_css)))
            except Exception as e:
                print('error:->', e)
            script = "window.scrollBy({x},{y});".format(x=msg_box.location.get('x', 0),
                                                        y=msg_box.location.get('y', 1000))
            print('script:', script)
            driver.execute_script(script)
            msg_list_css = "{0} {1}".format(box_css, "ul.msg-s-message-list>li")
            # print('msg_list_css:', msg_list_css)
            message_list = driver.find_elements_by_css_selector(msg_list_css)
            html = message_list[-1].get_attribute('innerHTML')
            # print('message_list:', html)
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
                    replied_date = replied_date.replace(minute=mi, hour=hr, day=d)
                    print('replied_date:', replied_date)
                try:
                    m = message_list[-1].find_element_by_css_selector('p.msg-s-event-listitem__body').text
                except Exception as e:
                    print(e)
                    pass
                if m:
                    message = m.strip()
                    print('message:', message)

    except Exception  as err:
        print('check connect error:', err)
        status = False

    driver.close()
    return status, replied_date, connect, message


def postconnect_browser(cur, taskrow, msgdetail):
    print('------------postconnect_browser-------------')
    email, password = get_user_email_pw(cur, taskrow[6])
    contact = get_db(cur, contact_select, (msgdetail[6],))
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
    # click on the send connect
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        driver.get(userhome)
        print('-----------finding--------pass_connect_btn----------------')
        try:
            connect_btn = wait.until(EC.visibility_of_element_located(
             (By.CSS_SELECTOR, "button.pv-s-profile-actions--connect")))
        except Exception as e:
            more_button_btn = wait.until(EC.visibility_of_element_located(
             (By.CSS_SELECTOR, "button.pv-s-profile-actions__overflow-toggle")))
            more_button_btn.click()
            connect_btn = wait.until(EC.visibility_of_element_located(
             (By.CSS_SELECTOR, "button.pv-s-profile-actions--connect")))
        connect_btn.click()

        # post the text in the popup
        box_css = """div#li-modal-container>div.modal-content-wrapper"""
        print('-------------------pass_connect_btn----------------')

        # add a note in popup
        addnote_css = """div.send-invite__actions>button.button-secondary-large"""
        btn_addnote = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, addnote_css)))
        btn_addnote.click()
        print('-------------------btn_addnote----------------')

        # text_box_css = "{0} {1}".format(box_css, "div.msg-form__compose-area>textarea[name='message']")
        text_box_css = "textarea#custom-message"
        print('text_box_css:', text_box_css)
        message_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, text_box_css)))
        message_box.send_keys(msgdetail[3])
        print('-------------------message_box----------------', msgdetail[3])

        message_box.send_keys(Keys.RETURN)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)

        # connect send in popup
        connect_css = "div.send-invite__actions>button.button-primary-large"
        btn_send = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, connect_css)))

        btn_send.click()

        time.sleep(IDLE_INTERVAL_IN_SECONDS)

    except Exception  as err:
        print('send connect error:', err)
        status = False
    driver.close()
    return status


def checkmessage_browser(cur, taskrow, msgdetail):
    email, password = get_user_email_pw(cur, taskrow[6])
    contact = get_db(cur, contact_select, (msgdetail[6],))
    print('contact:', contact)
    driver = get_driver(email, password)
    user_path = "/in/{0}/".format(contact[10])
    userhome = "{0}{1}".format(LINKEDIN_URL, user_path)
    print('userhome:', userhome)
    status = True
    replied_date = None
    message = ""
    # click on the send message
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        driver.get(userhome)
        message_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button.pv-s-profile-actions--message")))
        message_btn.click()
        box_css = """div.application-outlet>aside.msg-overlay-container div.msg-overlay-conversation-bubble div.msg-overlay-conversation-bubble__content-wrapper div.msg-s-message-list-container """
        #  textarea.ember-text-area msg-form__textarea"
        msg_box = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, box_css)))
        script = "window.scrollBy({x},{y});".format(x=msg_box.location.get('x', 0),
                                                    y=msg_box.location.get('y', 1000))
        print('script:', script)
        driver.execute_script(script)
        msg_list_css = "{0} {1}".format(box_css, "ul.msg-s-message-list>li")
        print('msg_list_css:', msg_list_css)
        message_list = driver.find_elements_by_css_selector(msg_list_css)
        html = message_list[-1].get_attribute('innerHTML')
        print('message_list:', html)
        if user_path in html:
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
                replied_date = replied_date.replace(minute=mi, hour=hr, day=d)
                print('replied_date:', replied_date)

            # get message
            try:
                m = message_list[-1].find_element_by_css_selector('p.msg-s-event-listitem__body').getText()
                print('-------------->', m)
            except Exception as e:
                print(e)
                pass
            # m = re.search(r'<p class="msg-s-event-listitem__body[^"]*">([^<]+)</p>', html)
            if m:
                message = m.group(1).strip()
                print('message:', message)

    except Exception  as err:
        print('send message error:', err)
        status = False

    driver.close()

    return status, replied_date, message


def find_contact_on_message_box(driver, contact):
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        new_message_open_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button.msg-overlay-bubble-header__control--new-convo-btn")))
        new_message_open_btn.click()
        input_search_field = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input.msg-connections-lookup__search-field")))
        input_search_field.send_keys(contact[15])
        input_search_field.send_keys(" ")
        input_search_field.send_keys(contact[13])
        input_search_field.send_keys(Keys.ENTER)
        input_search_field.send_keys(Keys.ENTER)
        input_search_field.send_keys(Keys.ENTER)
        input_search_field.send_keys(Keys.ENTER)
        input_search_field.send_keys(Keys.ENTER)

        search_list = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[@data-control-name='overlay.select_search_recipient']")))
        print(search_list)
        search_list.click()
    except Exception as e:
        print('---->', e)
        pass



def test_handle_connect():
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM app_bottask where status ='%s' or status='%s' order by id desc limit 1" % (bottask_status.QUEUED,
                                                                                                  bottask_status.PIN_CHECKING))
    row = cur.fetchone()
    print('row:', row)
    if row is not None and row[1] == bottask_type.POSTCONNECT:
        handle_checkconnect(cur, row)


if __name__ == "__main__":
    test_handle_connect()

"""
    require: python 3.6, selenium module, web driver
"""

from datetime import datetime, timedelta
import json
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bot_contact_detail import get_contact_ajax, get_contact_title
from bot_db import get_cursor, add_to_db, add_to_db2, get_user_email_pw
import bot_db as botdb
from bot_driver import login_linkedin_withwebdriver, get_driver, SEARCH_URL, \
    close_driver, get_browser_csrf_tocken, IDLE_INTERVAL_IN_SECONDS
from bot_search import   get_sale_nav_linkedid_id
from bot_sql import *
import bottask_status as botstatus
import bottask_type as tasktype
from captcha_solver import check_captcha
from freebotIP import get_ip, check_and_add_ip
from post_connect import handle_postconnect, handle_checkconnect
from post_message import handle_postmessage, handle_checkmessage


LINKEDIN_CONNECTIONS_URL = "https://www.linkedin.com/mynetwork/invite-connect/connections/"
IDLE_INTERVAL_IN_SECONDS = 5


months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
          "Sep", "Oct", "Nov", "Dec"]
days_of_week = ['sunday', 'monday', 'tuesday',
                'wednesday', 'thursday', 'friday', 'saturday']

FORCED_SHOWN_PIN = False


def get_task_row(cur, status=botstatus.QUEUED):
    # query must be changed to join with app_linkedinuser on (app_linkedinuser.id=app_bottask.owner_id)
    #  to get bot_ip field
    # and add condition bot_ip=current machine ip
    # just here, all other should be fine
    #
    sql = """SELECT bt.* FROM app_bottask bt join app_linkedinuser lu
    on(bt.owner_id=lu.id) where bt.status =%s and lu.bot_ip=%s order by id desc limit 1"""

    ip = get_ip()
    cur.execute(sql, (status, ip))
    row = cur.fetchone()
    return row


def get_task_row_pin(cur):
    return get_task_row(cur, botstatus.PIN_CHECKING)


def exist_user(wait):
    try:
        error_span = wait.until(EC.visibility_of_element_located(
            (By.ID, "session_key-login-error")))
        # session_password-login-error
        no_exist_user_alert = error_span.text
        print(no_exist_user_alert)
        return False
    except Exception as e:
        print('error:', e)
        return True


def check_password_correct(wait):
    print('checking if pw is not correct!')
    try:
        error_span = wait.until(EC.visibility_of_element_located(
            (By.ID, "session_password-login-error")))
        no_exist_user_alert = error_span.text
        print(no_exist_user_alert)
        return False
    except Exception as e:
        print('error:', e)
        # time.sleep(5)
        return True


def pinverify(wait, pincode=None,
              cur=None, owner_id=None, task_id=None, task_type=None):
    result = False
    no_pin_required = False
    try:
        pin_input_box = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input#verification-code")))

    except Exception as e:
        print('error:', e)
        if FORCED_SHOWN_PIN == False:
            no_pin_required = True
            return result, no_pin_required

    # wait for pin
    print("Please check your email address to verify.....")
    lastrun_date = datetime.now()
    completed_date = lastrun_date
    update_status = botstatus.PIN_REQUIRED
    cur.execute(bottask_update_query, (update_status, lastrun_date,
                                       completed_date, task_id, task_type, owner_id))
    taskrow = None
    while taskrow is None:
        taskrow = get_task_row_pin(cur)
        print('getting task:', taskrow)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)
    pindata = json.loads(taskrow[7])
    print('pindata:', pindata)
    pincode = pindata.get('pin', None)
    #pincode = input("Enter pin code:")
    if pincode is not None:
        update_status = botstatus.RUNNING
        cur.execute(running_update_query,
                    (update_status, task_id, task_type, owner_id))

        pin_submit_btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input#btn-primary")))
        pin_input_box.clear()
        pin_input_box.send_keys(pincode)
        pin_submit_btn.click()
        update_status = botstatus.DONE
        cur.execute(bottask_update_query, (update_status, lastrun_date,
                                           completed_date, taskrow[0], taskrow[1], taskrow[6]))
        result = True
        no_pin_required = True
    else:
        print('error:', e)
        no_pin_required = False
        update_status = botstatus.ERROR
        cur.execute(running_update_query,
                    (update_status, taskrow[0], taskrow[1], taskrow[6]))
    return result, no_pin_required


def read_mysql():
    cur = botdb.get_cursor()
    check_and_add_ip(cur)
    while True:
        print("checking....")
        row = get_task_row(cur, botstatus.QUEUED)
        if row is None:
            time.sleep(IDLE_INTERVAL_IN_SECONDS * 3)
            continue
        rows_count = 1
        task_type = ""
        owner_id = ""
        print(row)
        task_id = row[0]
        task_type = row[1]
        owner_id = row[6]
        if rows_count > 0:
            # cur.execute("SELECT * FROM app_bottask WHERE id=%s" % rows_count)
            # rows = cur.fetchall()
            print('task_type:', task_type)
            # LOGIN
            if task_type == tasktype.LOGIN:
                handle_login(cur, owner_id, task_id, task_type)

            # CONTACT
            elif task_type == tasktype.CONTACT:
                handle_new_contact(cur, owner_id, task_id, task_type)
                # handle_contact(cur, owner_id, task_id, task_type)

            # GET MESSAGES
            elif task_type == tasktype.MESSAGING:
                handle_message(cur, owner_id, task_id, task_type)

            # SEARCH
            elif task_type == tasktype.SEARCH:
                handle_search(cur, owner_id, task_id, task_type, row)

            # PIN VERIFY
            elif task_type == tasktype.PINVERIFY:
                # get pin
                handle_pinverify(cur, owner_id, task_id, task_type, row)
            # post message
            elif task_type == tasktype.POSTMESSAGE:
                handle_postmessage(cur, row)

            elif task_type == tasktype.CHECKMESSAGE:
                handle_checkmessage(cur, row)

            elif task_type == tasktype.POSTCONNECT:
                handle_postconnect(cur, row)

            elif task_type == tasktype.CHECKCONNECT:
                handle_checkconnect(cur, row)

            elif task_type == tasktype.UPDATECONTACT:
                handle_new_contact(cur, owner_id, task_id, task_type)
        time.sleep(IDLE_INTERVAL_IN_SECONDS)
    # connect.close()


def handle_login(cur, owner_id, task_id, task_type):
    email, password = get_user_email_pw(cur, owner_id)
    start_status = botstatus.RUNNING
    cur.execute(running_update_query,
                (start_status, task_id, task_type, owner_id))

    bot_result = login_linkedin(
        email, password, None, cur, owner_id, task_id, task_type)
    if(len(bot_result) == 4):
        return
    status = bot_result[0]
    lastrun_date = bot_result[1]
    completed_date = bot_result[2]
    cur.execute(bottask_update_query, (status, lastrun_date,
                                       completed_date, task_id, task_type, owner_id))


def handle_pinverify(cur, owner_id, task_id, task_type, taskrow):
    owner_id = taskrow[6]
    email, password = get_user_email_pw(cur, owner_id)
    cur.execute(running_update_query,
                (botstatus.RUNNING, task_id, task_type, owner_id))
    pindata = json.loads(taskrow[7])
    print('pindata:', pindata)
    status, lastrun_date, completed_date = login_linkedin(
        email, password, pindata['pin'])
    cur.execute(bottask_update_query, (status, lastrun_date,
                                       completed_date, task_id, task_type, owner_id))


def handle_message(cur, owner_id, task_id, task_type):
    email, password = get_user_email_pw(cur, owner_id)

    start_status = botstatus.RUNNING
    cur.execute(running_update_query,
                (start_status, task_id, task_type, owner_id))

    #bot_results = get_messages(email, password, cur, owner_id)
    bot_results = get_fastmessage(email, password, cur, owner_id)
    status = bot_results[0]
    lastrun_date = bot_results[1]
    completed_date = bot_results[2]
    cur.execute(bottask_update_query, (status, lastrun_date,
                                       completed_date, task_id, task_type, owner_id))
    print('Done.')


def handle_contact(cur, owner_id, task_id, task_type,):
        email, password = get_user_email_pw(cur, owner_id)

        start_status = botstatus.RUNNING
        cur.execute(running_update_query,
                    (start_status, task_id, task_type, owner_id))

        #bot_results = get_contacts(email, password, cur, owner_id)
        bot_results = get_fastcontacts(email, password, cur, owner_id)
        driver = bot_results[3]

        #get fast message
        #bot_results = get_messages(email, password, cur, owner_id, driver)
        bot_results = get_fastmessage(email, password, cur, owner_id, driver)
        status = bot_results[0]
        lastrun_date = bot_results[1]
        completed_date = bot_results[2]

        cur.execute(bottask_update_query, (status, lastrun_date,
                                           completed_date, task_id, task_type, owner_id))

        # update contacts with industry, location an dcouontry
        check_update_contact(driver, cur, owner_id)

        if driver:
            driver.close()


def handle_new_contact(cur, owner_id, task_id, task_type):
    email, password = get_user_email_pw(cur, owner_id)
    start_status = botstatus.RUNNING
    cur.execute(running_update_query, (start_status, task_id, task_type, owner_id))
    bot_results = get_new_contacts(email, password, cur, owner_id)
    driver = bot_results[3]
    new_contacts = bot_results[4]
    bot_results = get_new_message(email, password, cur, owner_id, driver, new_contacts)
    status = bot_results[0]
    lastrun_date = bot_results[1]
    completed_date = bot_results[2]
    cur.execute(bottask_update_query, (status, lastrun_date, completed_date, task_id, task_type, owner_id))
    check_update_contact(driver, cur, owner_id)
    if driver:
        driver.close()


def handle_search(cur, owner_id, task_id, task_type, taskrow):
    email, password = get_user_email_pw(cur, owner_id)
    print('owner_id:', owner_id)
    # extra_id
    if taskrow[8] is not None:

        search_id = int(taskrow[8])
        print('searchId:', type(taskrow[8]), search_id, ":")
        sql = search_keyword_query % (search_id)
    else:
        print('owner_id:', owner_id, taskrow[7])

        search_keyword_query2 = """SELECT * FROM connector_search
    WHERE owner_id=(%s) and (resultcount is NULL or resultcount = 0)
    order by searchdate desc limit 1"""
        sql = search_keyword_query2 % (owner_id)

    cur.execute(sql)
    print('sql:', sql)
    res = cur.fetchone()
    if res is None:
        print('record is none')
        start_status = botstatus.ERROR
        cur.execute(running_update_query,
                (start_status, task_id, task_type, owner_id))
        return

    search_id = res[0]

    search_mode = 0
    search_data = res[2]

    if search_data is None:
        if res[9] is None:
            search_mode = 1  # url_search
            search_data = res[11]
        else:
            search_mode = 2  # sales_search
            search_data = res[9]

    start_status = botstatus.RUNNING
    print('search_mode', search_mode)
    cur.execute(running_update_query,
                (start_status, task_id, task_type, owner_id))

    bot_results = search(email, password, search_data, cur,
                         search_id, owner_id, search_mode)

    status = bot_results[0]
    lastrun_date = bot_results[1]
    completed_date = bot_results[2]
    cur.execute(bottask_update_query, (status, lastrun_date,
                                       completed_date, task_id, task_type, owner_id))


def login_linkedin(email, password, pincode=None,
                   cur=None, owner_id=None, task_id=None, task_type=None):

    print("==== LOGIN =====")
    lastrun_date = datetime.now()
    completed_date = datetime.now()
    driver = login_linkedin_withwebdriver(email, password)
    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        # check if user is exist
        bot_status = botstatus.DONE
        if exist_user(wait):
            print("That user is an existing user.")

            if check_password_correct(wait):
                print('pw is correct')

                res = check_captcha(driver, task_id, task_type, owner_id, email, password)
                if res == False:
                    # driver.close()
                    return bot_status, lastrun_date, completed_date

                # pin code verification
                res, no_pin_required = pinverify(
                    wait, pincode, cur, owner_id, task_id, task_type)
                if res and no_pin_required:
                    completed_date = datetime.now()

                    close_driver(driver, email)
                    return bot_status, lastrun_date, completed_date, completed_date

                if (no_pin_required == False):
                    print("Pin to verify!")
                    if pincode is None:
                        bot_status = botstatus.PIN_REQUIRED
                    else:
                        bot_status = botstatus.PIN_INVALID
                else:
                    print("sucessfull login without pin code verification!")

            else:
                print('password is wrong')
                bot_status = botstatus.ERROR

        else:
            print("That user is not exist in Linkedin.")
            bot_status = botstatus.ERROR
        close_driver(driver, email)
        return bot_status, lastrun_date, completed_date

    except Exception as e:
        bot_status = botstatus.ERROR

        print(bot_status, ':', e)
        driver.close()
        return bot_status, lastrun_date, completed_date


def parse_connection_link(driver, connection_link):

        # get user-id
        get_link = connection_link.split("/")
        user_id = get_link[4]
        print('user_id:', user_id)

        # user id
        # linkedin_id_list.append(user_id)

        driver.get(connection_link)
        time.sleep(5)
        card_name = driver.find_element_by_class_name(
            "pv-top-card-section__name")
        actor_name = card_name.text
        try:
            actor_name.encode('utf-8')
        except Exception as errx:
            print('name err:', errx)

        print('card_name:', actor_name)
        time.sleep(5)
        # actor name
        # actor_name_list.append(actor_name.encode('utf-8'))

        actor_title_company = driver.find_element_by_class_name(
            "pv-top-card-section__headline").text
        title_company = ""
        actor_title = ""
        if " at " in actor_title_company:
            title_company = actor_title_company.split(" at ")
            actor_title = title_company[0]
            actor_company = title_company[1]
        else:
            actor_company = ""
            actor_title = actor_title_company

        print('title_company:', actor_name)
        # actor company & actor title
        # actor_company_list.append(actor_company)
        # actor_title_list.append(actor_title)

        # actor location
        actor_location = driver.find_element_by_class_name(
            "pv-top-card-section__location").text
        # actor_location_list.append(actor_location)
        print('actor_location:', actor_location)
        # latest_activity as connected date now,
        # when got message, get the last date sending date an dupdate
        # this field again
        industry = ""
        regex = r'industryName":"([^"]*)"'
        searchresult = re.search(regex, driver.page_source)
        if searchresult:
            industry = searchresult.group(1)

        print('industry:', industry)
        # shorten title
        actor_title = get_contact_title(actor_title)
        values = (actor_company, industry, actor_location,
                  actor_title, user_id, actor_name)
        print('values:', values)

        return values


def parse_connection_link_sales(driver, connection_link):

        # get user-id
        get_link = connection_link.split("/")
        sales_user_url = get_link[5]
        sales_user_name = sales_user_url.split(",")
        user_id = sales_user_name[0] + ',' + sales_user_name[1]
        print('user_id:', user_id)

        # user id
        # linkedin_id_list.append(user_id)

        driver.get(connection_link)
        time.sleep(5)
        card_name = driver.find_element_by_class_name("member-name")
        actor_name = card_name.text
        try:
            actor_name.encode('utf-8')
        except Exception as errx:
            print('name err:', errx)

        print('card_name:', actor_name)
        time.sleep(5)
        # actor name
        # actor_name_list.append(actor_name.encode('utf-8'))

        actor_title_company = driver.find_element_by_css_selector(
            "ul.positions li").text
        title_company = ""
        actor_title = ""
        if " at " in actor_title_company:
            title_company = actor_title_company.split(" at ")
            actor_title = title_company[0]
            try:
                actor_title.encode('utf-8')
            except Exception as errx:
                print('name err:', errx)
            actor_company = title_company[1]
            try:
                actor_company.encode('utf-8')
            except Exception as errx:
                print('name err:', errx)
        else:
            actor_company = ""
            actor_title = actor_title_company

        print('title_company:', actor_title)
        # actor company & actor title
        # actor_company_list.append(actor_company)
        # actor_title_list.append(actor_title)

        # actor location
        actor_location = driver.find_element_by_class_name(
            "location-industry .location").text

        # actor_location_list.append(actor_location)
        #print('actor_location:', actor_location)
        # latest_activity as connected date now,
        # when got message, get the last date sending date an dupdate
        # this field again
        try:
            industry = driver.find_element_by_class_name(
                "location-industry .industry").text
            industry.encode('utf-8')
        except Exception as errx:
            industry = ''
            print('name err:', errx)

        # print('industry:', industry)
        # shorten title
        actor_title = get_contact_title(actor_title)
        values = (actor_company, industry, actor_location,
                  actor_title, user_id, actor_name)

        print('values:', values)

        return values


def get_contacts(email, password, cur=None, owner_id=None):
    print("==== GET CONTACTS ======")
    lastrun_date = datetime.now()
    driver = login_linkedin_withwebdriver(email, password)
    try:
        time.sleep(15)
        # print(driver.page_source)
        # My Network contacts
        mynetwork_menu = driver.find_element_by_class_name(
            "nav-item--mynetwork")
        mynetwork_menu.click()
        time.sleep(5)
        see_all_link = driver.find_element_by_css_selector(
            "a.mn-connections-summary__see-all")
        see_all_link.click()
        time.sleep(5)
        total_connection_counts = driver.find_element_by_tag_name("h2")
        counts_text = total_connection_counts.text
        counts = counts_text.split(" ")
        act_count = counts[0]
        loop_range = int(act_count) // 40 + 1
        elem = driver.find_element_by_tag_name("html")
        print("loop_range:", loop_range)
        for i in range(loop_range):
            elem.send_keys(Keys.END)
            time.sleep(5)
        connections_times = driver.find_elements_by_css_selector(
            "time.time-badge")
        connection_time_list = []
        for connection_time in connections_times:
            connection_time_text = connection_time.text
            connection_time_split = connection_time_text.split(" ")
            connection_time_num = connection_time_split[1]
            connection_ago = connection_time_split[2]
            if "minute" in connection_ago:
                time_ago = datetime.today() - timedelta(minutes=int(connection_time_num))
            elif "hour" in connection_ago:
                time_ago = datetime.today() - timedelta(hours=int(connection_time_num))
            elif "day" in connection_ago:
                time_ago = datetime.today() - timedelta(days=int(connection_time_num))
            elif "week" in connection_ago:
                time_ago = datetime.today() - timedelta(weeks=int(connection_time_num))
            elif "month" in connection_ago:
                time_ago = datetime.today() - timedelta(days=int(connection_time_num) * 30)
            elif "year" in connection_ago:
                time_ago = datetime.today() - timedelta(days=int(connection_time_num) * 365)
            # connection time
            connection_time_list.append(str(time_ago))
        connections_lists = driver.find_elements_by_css_selector("a.mn-connection-card__link")
        connection_alink_lists = []
        for connction_link_list in connections_lists:
            connection_alink = connction_link_list.get_attribute('href')
            connection_alink_lists.append(connection_alink)
            print('connection_alink:', connection_alink)
        i = 0
        for connection_link in connection_alink_lists:
            print('get_contacts:', get_contacts)
            result = parse_connection_link(driver, connection_link)
            print('result:', result)
            values = result + (connection_time_list[i], botstatus.OLD_CONNECT_N, 1,
                               connection_time_list[i], owner_id,)

            i += 1
            if cur is not None:
                botdb.add_to_db(cur, getcontacts_query, *values)
            """
            cur.execute(getcontacts_query, (actor_company_list[i], "", actor_location_list[i], actor_title_list[
                            i], linkedin_id_list[i], actor_name_list[i], "", "22", "1", "1", connection_time_list[i], owner_id))

            """

        bot_status = botstatus.DONE
        # return linkedin_id_list, actor_name_list, actor_company_list, actor_title_list, actor_location_list, connection_time_list, bot_status, lastrun_date, completed_date

    except Exception as e:
        # bot_status = botstatus.ERROR
        bot_status = botstatus.DONE
        print("ERROR:", e)

    completed_date = datetime.now()
    #driver.close()
    return bot_status, lastrun_date, completed_date, driver


def remove_trim(value):
    return str(value).replace("'", "")


def get_new_contacts(email, password, cur=None, owner_id=None):
    driver = get_driver(email, password)
    print("==== GET NEW CONTACTS ======")
    lastrun_date = datetime.now()
    added_account_id = []
    print(" start time : ", datetime.now())
    try:
        driver.get(LINKEDIN_CONNECTIONS_URL)
        time.sleep(10)
        total_connection_counts = driver.find_element_by_tag_name("h2")
        counts_text = total_connection_counts.text
        counts = counts_text.split(" ")
        cnt_all_connections = counts[0].replace(',', '')
        csrf_tocken = get_browser_csrf_tocken(driver)
        driver.execute_script("""
          var element = document.createElement('div');
          element.id = "interceptedResponse";
          element.appendChild(document.createTextNode(""));
          document.body.appendChild(element);
          var xhttp = new XMLHttpRequest();
          xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
              document.getElementById("interceptedResponse").innerHTML = this.responseText;
            }
          };
          xhttp.open("GET", "https://www.linkedin.com/voyager/api/relationships/connections?count=""" + cnt_all_connections + """&sortType=RECENTLY_ADDED&start=0", true);
          xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
          xhttp.send();""")
        time.sleep(5)
        responsedata = driver.find_element_by_id('interceptedResponse').text
        targetjsondata = json.loads(responsedata)
        targetjsondata = targetjsondata['elements']
        for itemdata in targetjsondata:
            firstName = remove_trim(itemdata['miniProfile']['firstName'])
            lastName = remove_trim(itemdata['miniProfile']['lastName'])
            occupation = remove_trim(itemdata['miniProfile']['occupation'])
            publicIdentifier = remove_trim(itemdata['miniProfile']['publicIdentifier'])
            createdAt = itemdata['createdAt']
            createdAtTime = datetime.fromtimestamp(int(str(createdAt)[0:10]))
            actor_title = ""
            actor_company = ""
            if " at " in occupation:
                title_company = occupation.split(" at ")
                actor_title = title_company[0]
                actor_company = title_company[1]
            else:
                actor_company = ""
                actor_title = occupation
            actor_title = get_contact_title(remove_trim(actor_title))
            values = (actor_company, "", "", actor_title,
                      publicIdentifier, firstName + ' ' + lastName,)
            values = values + \
                (createdAtTime, str(botstatus.OLD_CONNECT_N),
                 '1', createdAtTime, str(owner_id),)
            if cur is not None:
                new_contact = botdb.update_or_insert_contact(cur, getcontacts_query, *values)
                if new_contact:
                    added_account_id.append(new_contact)
        print(' Number of connections : ', len(added_account_id))
        print(" end time   : ", datetime.now())
        print("==== GET CONTACTS ======")
        bot_status = botstatus.DONE
    except Exception as e:
        # bot_status = botstatus.ERROR
        bot_status = botstatus.DONE
        print("ERROR:", e)
    completed_date = datetime.now()
    return bot_status, lastrun_date, completed_date, driver, added_account_id


def get_fastcontacts(email, password, cur=None, owner_id=None):
    driver = get_driver(email, password)
    print("==== GET CONTACTS ======")
    lastrun_date = datetime.now()
    print(" start time : ", datetime.now())
    try:
        driver.get(LINKEDIN_CONNECTIONS_URL)
        time.sleep(10)
        total_connection_counts = driver.find_element_by_tag_name("h2")
        counts_text = total_connection_counts.text
        counts = counts_text.split(" ")
        cnt_all_connections = counts[0].replace(',', '')
        csrf_tocken = get_browser_csrf_tocken(driver)
        #############################################################################################################################
        driver.execute_script("""
          var element = document.createElement('div');
          element.id = "interceptedResponse";
          element.appendChild(document.createTextNode(""));
          document.body.appendChild(element);
          var xhttp = new XMLHttpRequest();
          xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
              document.getElementById("interceptedResponse").innerHTML = this.responseText;
            }
          };
          xhttp.open("GET", "https://www.linkedin.com/voyager/api/relationships/connections?count=""" + cnt_all_connections + """&sortType=RECENTLY_ADDED&start=0", true);
          xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
          xhttp.send();""")
        #############################################################################################################################
        time.sleep(3)
        responsedata = driver.find_element_by_id('interceptedResponse').text
        #print('responsedata :', responsedata)
        targetjsondata = json.loads(responsedata)
        print('----------------targetjsondata------------------> :', targetjsondata)
        targetjsondata = targetjsondata['elements']
        for itemdata in targetjsondata:
            firstName = remove_trim(itemdata['miniProfile']['firstName'])
            lastName = remove_trim(itemdata['miniProfile']['lastName'])
            occupation = remove_trim(itemdata['miniProfile']['occupation'])
            publicIdentifier = remove_trim(itemdata['miniProfile']['publicIdentifier'])
            createdAt = itemdata['createdAt']
            createdAtTime = datetime.fromtimestamp(int(str(createdAt)[0:10]))
            actor_title = ""
            actor_company = ""
            if " at " in occupation:
                title_company = occupation.split(" at ")
                actor_title = title_company[0]
                actor_company = title_company[1]
            else:
                actor_company = ""
                actor_title = occupation
            actor_title = get_contact_title(remove_trim(actor_title))
            values = (actor_company, "", "", actor_title,
                      publicIdentifier, firstName + ' ' + lastName,)
            values = values + \
                (createdAtTime, str(botstatus.OLD_CONNECT_N),
                 '1', createdAtTime, str(owner_id),)
            if cur is not None:
                botdb.add_to_db2(cur, getcontacts_query, *values)
        print(' Number of connections : ', len(targetjsondata))
        print(" end time   : ", datetime.now())
        print("==== GET CONTACTS ======")
        bot_status = botstatus.DONE

    except Exception as e:
        # bot_status = botstatus.ERROR
        bot_status = botstatus.DONE
        print("ERROR:", e)
    completed_date = datetime.now()
    # driver.close()
    return bot_status, lastrun_date, completed_date, driver


def get_contacts_by_ownerid(cur, owner_id):
    sql = """select id, linkedin_id from messenger_inbox where owner_id=%s"""
    cur.execute(sql, (owner_id))
    return cur.fetchall()


def get_new_message(email, password, cursor=None, owner_id=None,
                    driver=None, new_contacts=None):
    if driver is None:
        driver = get_driver(email, password)
    print("==== GET New MESSAGE ======")
    lastrun_date = datetime.now()
    is_read = 1
    is_direct = 1
    is_sent = 1
    driver.find_element_by_id('feed-nav-item').click()
    time.sleep(10)
    profile_link = driver.find_element_by_css_selector("a.feed-identity-module__actor-link")
    mylinkedin_id = profile_link.get_attribute('href').split('/')[-2]
    print(" start time : ", datetime.now())
    try:
        csrf_tocken = get_browser_csrf_tocken(driver)
        pagingtotal = 10000
        createdBefore = ''
        createdAts = []
        elements = []
        contactIDs = []
        # contactslist_from_db = new_contacts
        contactslist_from_db = get_contacts_by_ownerid(cursor, owner_id)
        contactslist_from_db_list = dict()
        for linkedinid_from_db in contactslist_from_db:
            contactslist_from_db_list[linkedinid_from_db[1]] = linkedinid_from_db[0]
        while True:
            if(pagingtotal == 0):
                break
            createdBeforeStr = ''
            if(createdBefore != ''):
                createdBeforeStr = '&createdBefore=' + createdBefore
            driver.execute_script("""
                  var element = document.createElement('div');
                  element.id = "interceptedConversationResponse";
                  element.appendChild(document.createTextNode(""));
                  document.body.appendChild(element);
                  var xhttp = new XMLHttpRequest();
                  xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                      document.getElementById("interceptedConversationResponse").innerHTML = this.responseText;
                    }
                  };
                  xhttp.open("GET", "https://www.linkedin.com/voyager/api/messaging/conversations?keyVersion=LEGACY_INBOX""" + createdBeforeStr + """", true);
                  xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                  xhttp.setRequestHeader('X-Restli-Protocol-Version', '2.0.0')
                  xhttp.setRequestHeader('X-Li-Lang', 'en_US')
                  xhttp.send();
                """)
            time.sleep(2)
            conversationListText = driver.find_element_by_id( 'interceptedConversationResponse').text
            strfindurn = 'urn:li:fs_conversation:'
            strcreatedat = '"createdAt":'
            participants = '"participants":'
            strtotal = '"total":'
            while conversationListText.find(strfindurn) != -1:
                conversationListText = conversationListText[conversationListText.find(strfindurn) + len(strfindurn):]
                converseID = conversationListText[0:conversationListText.find('"')]
                conversationListText = conversationListText[conversationListText.find(strcreatedat) + len(strcreatedat):]
                createdAtItem = conversationListText[0:conversationListText.find(',')]
                conversationListText = conversationListText[conversationListText.find(participants) + len(participants):]
                conversationListText = conversationListText[conversationListText.find('"publicIdentifier":"') + len('"publicIdentifier":"'):]
                publicIdentifier = conversationListText[0:conversationListText.find('"')]
                print('publicIdentifier:', publicIdentifier)
                if publicIdentifier != 'UNKNOWN':
                    if publicIdentifier in contactslist_from_db_list:
                        contact = contactslist_from_db_list[publicIdentifier]
                        elementitem = []
                        elementitem.append(converseID)
                        elementitem.append(publicIdentifier)
                        elementitem.append(contact)
                        elements.append(elementitem)
                        driver.execute_script("""
                              var element = document.createElement('div');
                              element.id = "interceptedConversationResponse_""" + converseID + """";
                              element.appendChild(document.createTextNode(""));
                              document.body.appendChild(element);
                              var xhttp = new XMLHttpRequest();
                              xhttp.onreadystatechange = function() {
                                if (this.readyState == 4 && this.status == 200) {
                                  document.getElementById("interceptedConversationResponse_""" + converseID + """").innerHTML = this.responseText;
                                }
                              };
                              xhttp.open("GET", "https://www.linkedin.com/voyager/api/messaging/conversations/""" + str(converseID) + """/events", true);
                              xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                              xhttp.setRequestHeader('X-Restli-Protocol-Version', '2.0.0')
                              xhttp.setRequestHeader('X-Li-Lang', 'en_US')
                              xhttp.send();
                            """)
                createdAts.append(createdAtItem)

            conversationListText = conversationListText[conversationListText.find(strtotal) + len(strtotal):]
            pagingtotal = int(conversationListText[0:conversationListText.find(',')])
            if(pagingtotal !=0):
                createdAts.sort()
                createdBefore = str(int(createdAts[0]) -1)
            createdAts = []

        print('element count : ', len(elements))
        time.sleep(10)
        print('get New message conversations start : ', datetime.now())
        completed_date = datetime.now()
        updated_at = datetime.now()
        for conversation in elements:
            strresponse = driver.find_element_by_id('interceptedConversationResponse_' + conversation[0]).text
            jsondata = json.loads(strresponse, strict=False)
            converselements = jsondata['elements']
            conversations = []
            contact_id = conversation[2]
            linkedin_id = ""
            for conversitem in converselements:
                # get linkedin_id
                if 'publicIdentifier' in conversitem and (
                    conversitem['publicIdentifier'] != str(mylinkedin_id)):
                    linkedin_id = conversitem['publicIdentifier']
                    print('linkedin_id:', linkedin_id)
                subtype = conversitem['subtype']
                if(subtype == 'MEMBER_TO_MEMBER'):
                    message_created_at = conversitem['createdAt']
                    message_body = conversitem['eventContent']['com.linkedin.voyager.messaging.event.MessageEvent']['body']
                    message_from = conversitem['from']['com.linkedin.voyager.messaging.MessagingMember']['miniProfile']['publicIdentifier']
                    if message_created_at != '':
                        if str(mylinkedin_id) == str(message_from):
                            is_direct = 1
                        else:
                            is_direct = 0
                        if contact_id is None or contact_id == 0:
                            if message_from in contactslist_from_db_list:
                                contact_id  = contactslist_from_db_list[message_from]
                            elif linkedin_id != "" and (linkedin_id in contactslist_from_db_list):
                                contact_id  = contactslist_from_db_list[linkedin_id]
                        message_created_at_db = datetime.fromtimestamp(int(str(message_created_at)[0:10]))
                        conversations.append((str(message_body), is_direct, message_created_at_db, ))
            for msg_body, is_direct, msg_date in conversations:
                values = (completed_date, updated_at, msg_body,
                          msg_date, 1, contact_id , owner_id,
                          is_direct, is_read, is_sent)
                print('values 2:', values)
                if cursor is not None:
                    botdb.update_or_insert_message(cursor, getmessages_query, *values)
        print('get new message end : ', datetime.now())
        bot_status = botstatus.DONE
    except Exception as e:
        print("ERROR:", e)
        bot_status = botstatus.DONE

    completed_date = datetime.now()
    # driver.close()
    return bot_status, lastrun_date, completed_date


def get_fastmessage(email, password, cursor=None, owner_id=None,
                    driver=None):
    if driver is None:
        driver = get_driver(email, password)

    print("==== GET FAST MESSAGE ======")
    # print("login start")
    lastrun_date = datetime.now()
    is_read = 1
    is_direct = 1
    is_sent = 1
    #driver = login_linkedin_withwebdriver(email, password)
    # driver = marionette_driver(headless=False, loadsession=True)
    # back to home
    driver.find_element_by_id('feed-nav-item').click()
    #driver.get(LINKEDIN_URL)
    time.sleep(10)
    profile_link = driver.find_element_by_css_selector("a.feed-identity-module__actor-link")
    mylinkedin_id = profile_link.get_attribute('href').split('/')[-2]
    print(" start time : ", datetime.now())
    try:
        """
        request_cookies_browser = driver.get_cookies()
        JSESSIONID = driver.get_cookie('JSESSIONID')
        csrf_tocken = JSESSIONID['value']
        """
        csrf_tocken = get_browser_csrf_tocken(driver)
        pagingtotal = 10000
        createdBefore = ''
        createdAts = []
        elements = []
        contactIDs = []
        contactslist_from_db = get_contacts_by_ownerid(cursor, owner_id)
        contactslist_from_db_list = dict()
        for linkedinid_from_db in contactslist_from_db:
            contactslist_from_db_list[linkedinid_from_db[1]] = linkedinid_from_db[0]
        while True:
            if(pagingtotal == 0):
                break
            createdBeforeStr = ''
            if(createdBefore != ''):
                createdBeforeStr = '&createdBefore=' + createdBefore
            driver.execute_script("""
                  var element = document.createElement('div');
                  element.id = "interceptedConversationResponse";
                  element.appendChild(document.createTextNode(""));
                  document.body.appendChild(element);

                  var xhttp = new XMLHttpRequest();

                  xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {

                      document.getElementById("interceptedConversationResponse").innerHTML = this.responseText;
                    }
                  };
                  xhttp.open("GET", "https://www.linkedin.com/voyager/api/messaging/conversations?keyVersion=LEGACY_INBOX""" + createdBeforeStr + """", true);
                  xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                  xhttp.setRequestHeader('X-Restli-Protocol-Version', '2.0.0')
                  xhttp.setRequestHeader('X-Li-Lang', 'en_US')
                  xhttp.send();
                """)
            #############################################################################################################################
            time.sleep(2)
            conversationListText = driver.find_element_by_id( 'interceptedConversationResponse').text
            # print(" conversationListText : ", conversationListText)
            strfindurn = 'urn:li:fs_conversation:'
            strcreatedat = '"createdAt":'
            participants = '"participants":'
            strtotal = '"total":'
            while conversationListText.find(strfindurn) != -1:
                conversationListText = conversationListText[conversationListText.find(strfindurn) + len(strfindurn):]
                converseID = conversationListText[0:conversationListText.find('"')]
                conversationListText = conversationListText[conversationListText.find(strcreatedat) + len(strcreatedat):]
                createdAtItem = conversationListText[0:conversationListText.find(',')]
                #get participants publicIdentifier
                conversationListText = conversationListText[conversationListText.find(participants) + len(participants):]
                conversationListText = conversationListText[conversationListText.find('"publicIdentifier":"') + len('"publicIdentifier":"'):]
                publicIdentifier = conversationListText[0:conversationListText.find('"')]
                print('publicIdentifier:', publicIdentifier)
                if publicIdentifier != 'UNKNOWN':
                    #if publicIdentifier in contactslist_from_db_list:
                    if publicIdentifier in contactslist_from_db_list:
                        contact = contactslist_from_db_list[publicIdentifier]
                        elementitem = []
                        elementitem.append(converseID)
                        elementitem.append(publicIdentifier)
                        elementitem.append(contact)
                        elements.append(elementitem)
                        #############################################################################################################################
                        driver.execute_script("""
                              var element = document.createElement('div');
                              element.id = "interceptedConversationResponse_""" + converseID + """";
                              element.appendChild(document.createTextNode(""));
                              document.body.appendChild(element);

                              var xhttp = new XMLHttpRequest();

                              xhttp.onreadystatechange = function() {
                                if (this.readyState == 4 && this.status == 200) {

                                  document.getElementById("interceptedConversationResponse_""" + converseID + """").innerHTML = this.responseText;
                                }
                              };

                              xhttp.open("GET", "https://www.linkedin.com/voyager/api/messaging/conversations/""" + str(converseID) + """/events", true);
                              xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                              xhttp.setRequestHeader('X-Restli-Protocol-Version', '2.0.0')
                              xhttp.setRequestHeader('X-Li-Lang', 'en_US')
                              xhttp.send();

                            """)
                        #############################################################################################################################

                        # elements.append(converseID)
                        # contactIDs.append(publicIdentifier)
                createdAts.append(createdAtItem)
            conversationListText = conversationListText[conversationListText.find(strtotal) + len(strtotal):]
            pagingtotal = int(conversationListText[0:conversationListText.find(',')])
            if(pagingtotal !=0):
                createdAts.sort()
                createdBefore = str(int(createdAts[0]) -1)
            #initialize createdAt
            createdAts = []
        print('element count : ', len(elements))
        time.sleep(10)
        print('get fastmessage conversations start : ', datetime.now())
        completed_date = datetime.now()
        updated_at = datetime.now()
        #getting all conversations
        for conversation in elements:
            strresponse = driver.find_element_by_id('interceptedConversationResponse_' + conversation[0]).text
            jsondata = json.loads(strresponse, strict=False)
            converselements = jsondata['elements']
            conversations = []
            contact_id = conversation[2]
            linkedin_id = ""
            for conversitem in converselements:
                # get linkedin_id
                if 'publicIdentifier' in conversitem and (
                    conversitem['publicIdentifier'] != str(mylinkedin_id)):
                    linkedin_id = conversitem['publicIdentifier']
                    print('linkedin_id:', linkedin_id)

                subtype = conversitem['subtype']
                if(subtype == 'MEMBER_TO_MEMBER'):
                    print('============= converstation MEMBER_TO_MEMBER =============')
                    message_created_at = conversitem['createdAt']
                    message_body = conversitem['eventContent']['com.linkedin.voyager.messaging.event.MessageEvent']['body']
                    message_from = conversitem['from']['com.linkedin.voyager.messaging.MessagingMember']['miniProfile']['publicIdentifier']
                    if message_created_at != '':
                        if str(mylinkedin_id) == str(message_from):
                            is_direct = 1
                            """ no need for this case
                            ########################################## insert mylinedin id to messenger_inbox table ############################
                            if mylinkedin_id in contactslist_from_db_list:
                                is_direct = 1
                            else:
                                firstName = conversitem['from']['com.linkedin.voyager.messaging.MessagingMember']['miniProfile']['firstName']
                                lastName = conversitem['from']['com.linkedin.voyager.messaging.MessagingMember']['miniProfile']['lastName']
                                occupation = conversitem['from']['com.linkedin.voyager.messaging.MessagingMember']['miniProfile']['occupation']
                                actor_title =""
                                actor_company =""
                                if " at " in occupation:
                                    title_company = occupation.split(" at ")
                                    actor_title = title_company[0]
                                    actor_company = title_company[1]
                                else:
                                    actor_company = ""
                                    actor_title = occupation
                                actor_title = get_contact_title(actor_title)
                                values = (actor_company, "", "", actor_title, mylinkedin_id, firstName + ' ' + lastName,)
                                values = values + (datetime.now(), str(botstatus.OLD_CONNECT_N), '1', datetime.now(), str(owner_id),)
                                if cursor is not None:
                                    botdb.add_to_db2(cursor, getcontacts_query, *values)
                                    mycontact = get_contact_by_uid(cursor, mylinkedin_id, owner_id)
                                    contactslist_from_db_list[mylinkedin_id] = mycontact[0]
                            ########################################## insert mylinedin id to messenger_inbox table ############################
                            """
                        else:
                            is_direct = 0
                        if contact_id is None or contact_id == 0:
                            if message_from in contactslist_from_db_list:
                                contact_id  = contactslist_from_db_list[message_from]
                            elif linkedin_id != "" and (linkedin_id in contactslist_from_db_list):
                                contact_id  = contactslist_from_db_list[linkedin_id]
                        message_created_at_db = datetime.fromtimestamp(int(str(message_created_at)[0:10]))
                        conversations.append((str(message_body), is_direct, message_created_at_db, ))
            for msg_body, is_direct, msg_date in conversations:
                values = (completed_date, updated_at, msg_body,
                          msg_date, 1, contact_id , owner_id,
                          is_direct, is_read, is_sent)
                print('values 2:', values)
                if cursor is not None:
                    botdb.add_to_db2(cursor, getmessages_query, *values)
        print('get fastmessage end : ', datetime.now())
        bot_status = botstatus.DONE
        # return linkedin_id_list, actor_name_list, actor_company_list, actor_title_list, actor_location_list, connection_time_list, bot_status, lastrun_date, completed_date

    except Exception as e:
        print("ERROR:", e)
        bot_status = botstatus.DONE

    completed_date = datetime.now()
    # driver.close()

    return bot_status, lastrun_date, completed_date


def get_message_created_date(message_date):
    today = datetime.now()

    y = today.year
    d = today.day
    m = today.month

    print('message_date parsing:', message_date)

    if message_date == '' or message_date.capitalize() == 'Today':
        pass
    elif message_date.lower() in days_of_week:
        today = datetime.now()
        target_day = days_of_week.index(message_date.lower())
        delta_day = target_day - today.isoweekday()

        if delta_day >= 0:
            delta_day -= 7  # go back 7 days

        today = today + timedelta(days=delta_day)

    else:
        # 12/16/2016
        match = re.search(r'(\d\d).(\d\d).([\d]+)', message_date)
        if match:
            m = int(match.group(1))
            d = int(match.group(2))
            y = int(match.group(3))
            if y < 2000:
                y = y + 2000
            today = today.replace(year=y, month=m, day=d)

        else:

            date_list = message_date.split(' ')
            day = int(date_list[1])
            mon = date_list[0].capitalize()[:3]
            #print('mon:', mon, mon in months)
            month = months.index(mon) + 1
            #print('month:', month)

            if len(date_list) == 3:
                y = int(date_list[2])
            else:
                if month > m:
                    y = y - 1
                if month == m and day > d:
                    y = y - 1

                today = today.replace(year=y, month=month, day=day)

    return today


def get_message_created_time(message_date, message_time):
    print('get_message_created_time:', message_date, message_time)

    msg_date = get_message_created_date(message_date)
    print('msg_date:', msg_date)

    if message_time != '':
        print(message_time)
        msg_time = message_time.split(' ')[0]
        hour = int(msg_time.split(':')[0])
        minute = int(msg_time.split(':')[1])

        if message_time.split(' ')[1] == 'PM':
            hour += 12
    else:
        hour = 0
        minute = 0

    created_at = msg_date.replace(hour=hour, minute=minute)
    return created_at


def get_contact_by_uid(cur, uid, owner_id):
    sql = """select * from messenger_inbox where linkedin_id=%s and owner_id=%s"""
    cur.execute(sql, (uid, owner_id))
    return cur.fetchone()


def get_messages(email, password,  cur=None, owner_id=None, driver=None):

    print("==== GET MESSAGES ======")
    lastrun_date = datetime.now()
    is_read = 1
    is_direct = 1
    is_sent = 1
    if driver is None:
        driver = login_linkedin_withwebdriver(email, password)

    try:
        verify_login(driver)
        time.sleep(3)

        # Reading messages
        messageing_menu = driver.find_element_by_css_selector(
            "span#messaging-tab-icon")
        messageing_menu.click()
        time.sleep(10)

        elem = driver.find_element_by_tag_name("html")
        elem.send_keys(Keys.END)

        messaging_ul = driver.find_element_by_class_name(
            "msg-conversations-container__conversations-list")
        driver.execute_script(
            'arguments[0].scrollDown = arguments[0].scrollHeight', messaging_ul)
        messaging_list = driver.find_elements_by_css_selector(
            "li.msg-conversation-listitem")

        for messaging in messaging_list:
            #created_at_time = messaging.find_element_by_css_selector("time.msg-conversation-listitem__time-stamp")
            #created_at = created_at_time.text
            # check for overlay box
            try:
                artdeco = driver.find_element_by_css_selector(
                    '#artdeco-modal-outlet>artdeco-modal-overlay')
                buton = artdeco.find_element_by_class_name('artdeco-dismiss')
                buton.click()
                time.sleep(IDLE_INTERVAL_IN_SECONDS)
            except Exception as err:
                print('overly err:', err)

            msg_list_css = "msg-conversation-listitem__link"
            messaging_member = messaging.find_element_by_class_name(
                msg_list_css)
            messaging_member.click()
            driver.execute_script("window.scrollBy(0, 1000);")

            # if this is the connected
            contact_uid = ""
            contact_path = ""
            try:
                a_profile = driver.find_element_by_class_name(
                    "msg-thread__topcard-btn")
                contact_uid = a_profile.get_attribute('href').split('/')[-2]
            except Exception as err:
                print('not a connected:', err)

            if contact_uid == "":
                continue

            contact_path = '/in/{0}'.format(contact_uid)
            contact = get_contact_by_uid(cur, contact_uid, owner_id)
            if contact is None:
                print('no contact:', contact_uid, contact_path)
                continue

            """
            try:
                messaging_text_div = driver.find_element_by_class_name("msg-spinmail-thread__message-body")
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', messaging_text_div)
                messaging_text_ps = messaging_text_div.find_elements_by_tag_name("p")

                message = ''
                for messaging_text_p in messaging_text_ps:
                    messaging_text = messaging_text_p.text
                    words = messaging_text.split(' ')
                    i = 0
                    for word in words:
                        if i > 0:
                            message += ' '
                        message = message + word.strip()
                        i += 1

                words = message.split("'")
                message = ''
                i = 0
                for word in words:
                    if i > 0:
                        message = message + '\"' + word
                    else:
                        message = message + word
                    i += 1

                # add to db
                completed_date = datetime.now()
                updated_at = datetime.now()

                if created_at.split(' ')[1] and (created_at.split(' ')[1] == 'AM' or created_at.split(' ')[1] == 'PM'):
                    created_at = get_message_created_time('', created_at)
                else:
                    created_at = get_message_created_time(created_at, '')

                values = (created_at, updated_at, message, completed_date, type, owner_id, is_direct, is_read)
                if cur is not None:
                    botdb.add_to_db(cur, getmessages_query, *values)
                else:
                    print('values 1:', values)

            except Exception as e:
            """

            messaging_div = driver.find_element_by_class_name(
                "msg-s-message-list-container")
            messaging_ul = messaging_div.find_element_by_css_selector(
                "ul.msg-s-message-list")
            driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', messaging_ul)
            message_list = messaging_ul.find_elements_by_css_selector(
                "li.msg-s-message-list__event")

            create_at_dates = []
            prev_create_at_date = ''
            prev_create_at_time = ''
            messages = []
            i = 0
            for message_li in message_list:
                print('message_li:', message_li.get_attribute(('innerHTML')))

                try:
                    create_at_date_li = message_li.find_element_by_css_selector(
                        "time.msg-s-message-list__time-heading")
                    create_at_date = create_at_date_li.text
                    prev_create_at_date = create_at_date

                except Exception as e:
                    create_at_date = prev_create_at_date

                try:
                    created_at_time_li = message_li.find_element_by_css_selector(
                        "time.msg-s-message-group__timestamp")
                    created_at_time = created_at_time_li.text

                    prev_create_at_time = created_at_time
                except Exception as e:
                    created_at_time = prev_create_at_time

                created_date = get_message_created_time(
                    create_at_date, created_at_time)
                # msg-s-event-listitem__message-bubble
                #print('message_li:', message_li.get_attribute('innerHTML'))
                is_direct = 1
                if contact_path in message_li.get_attribute('innerHTML'):
                    is_direct = 0

                try:
                    messaging_text_div = message_li.find_element_by_class_name(
                        "msg-s-event-listitem__message-bubble")
                    driver.execute_script(
                        'arguments[0].scrollTop = arguments[0].scrollHeight', messaging_text_div)
                    messaging_text_p = messaging_text_div.find_element_by_class_name(
                        "msg-s-event-listitem__body")
                    messaging_text = messaging_text_p.text
                    message = parse_messaging_txt(messaging_text)

                    messages.append((message, is_direct))
                    create_at_dates.append(created_date)

                    i += 1
                except Exception as err:
                    print('error:', err)

            completed_date = datetime.now()
            updated_at = datetime.now()

            print('create_at_dates:', create_at_dates)
            print('messages:', messages)
            for k in range(0, len(messages)):
                message, is_direct = messages[k]
                # testing only
                contact_id = 45
                if contact and len(contact) > 0:
                    contact_id = contact[0]

                values = (completed_date, updated_at, str(
                    message), create_at_dates[k], 1, contact_id, owner_id, is_direct, is_read, is_sent)
                print('values 2:', values)
                if cur is not None:
                    botdb.add_to_db2(cur, getmessages_query, *values)

        time.sleep(5)
        bot_status = botstatus.DONE

    except Exception as e:
        # bot_status = botstatus.ERROR
        # just consider all are okay now
        bot_status = botstatus.DONE
        print("ERROR:",  e)

    driver.close()

    completed_date = datetime.now()
    return bot_status, lastrun_date, completed_date


def parse_messaging_txt(messaging_text):
    #return messaging_text

    message = ''
    words = messaging_text.split(' ')
    j = 0
    for word in words:
        if j > 0:
            message += ' '
        message = message + word.strip()
        j += 1

    words = message.split("'")
    message = ''
    j = 0
    for word in words:
        if j > 0:
            message = message + '\"' + word
        else:
            message = message + word
        j += 1
    return message


def parse_search_result(driver, limit):
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
    # range_count = 300

    parse_urls = {}
    print('parsing url:')
    count = 0
    for _ in range(range_count):
        time.sleep(3)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)
        search_list = driver.find_elements_by_class_name(
            "search-result__result-link")
        for tag in search_list:
            url = tag.get_attribute('href')
            if url in parse_urls or 'result' in url:
                continue

            uid = url.split('/')[-2]
            parse_urls[uid] = 1
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

    return parse_urls


# Search
def search(email, password, search_data, cur=None, search_id=None, owner_id=None, search_mode=0,
           limit=750):

    driver = get_driver(email, password, force_login=True)
    lastrun_date = datetime.now()

    """ do not need now, default 1000
    cur.execute(get_membership_by_owner_id, owner_id)
    member_ship = cur.fetchone()
    print('-----------------------', member_ship)

    # max_search = member_ship[4] # max_search mean number of search
    max_search =  500
    if member_ship:
        max_search = member_ship[10] # max_search_result
    """

    limit = 1000
    try:
        if search_mode == 0:
            if 'feed' not in driver.current_url:
                driver.get(SEARCH_URL)
            time.sleep(5)
            # search connection
            search_input = driver.find_element_by_xpath(
                "/html/body/nav/div/form/div/div/div/artdeco-typeahead-deprecated/artdeco-typeahead-deprecated-input/input")
            keyword = search_data
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)
            print("-------click search button-----------")
            parse_urls = parse_search_result(driver, limit)
            get_search_contact(parse_urls, driver, cur, owner_id, search_id)
            bot_status = botstatus.DONE
        elif search_mode == 1:
            time.sleep(5)
            driver.get(search_data)
            print("-------Go to search url-----------")
            parse_urls = parse_search_result(driver, limit)
            get_search_contact(parse_urls, driver, cur, owner_id, search_id)
            bot_status = botstatus.DONE
        else:
            time.sleep(IDLE_INTERVAL_IN_SECONDS)
            driver.get(search_data)
            print("-------Go to sales navigator search url-----------")
            time.sleep(10)
            try:
                total_resultcounts_tag = driver.find_element_by_css_selector(
                    ".TR .spotlight-result-count")
            except:
                print("search has not result")
                values = (0, search_id, )
                add_to_db2(cur, search_update_query, *values)
                bot_status = botstatus.DONE
                driver.close()
                completed_date = datetime.now()
                return bot_status, lastrun_date, completed_date

            total_resultcounts = total_resultcounts_tag.text
            real_counts = 0
            if total_resultcounts[-1:] == 'M':
                real_counts = float(total_resultcounts[:-1]) * 1000000
            elif total_resultcounts[-1:] == 'K':
                real_counts = float(total_resultcounts[:-1]) * 1000
            else:
                real_counts = int(total_resultcounts)
            print('counts:', int(real_counts))
            if real_counts == 0:
                print("search has not result")
                values = (0, search_id, )
                add_to_db2(cur, search_update_query, *values)
                bot_status = botstatus.DONE
                driver.close()
                completed_date = datetime.now()
                return bot_status, lastrun_date, completed_date
            offset = 25
            range_count = int(real_counts) // offset + 1
            print('range_count:', range_count)
            range_count = 10
            print('parsing profile:')
            count = 0
            for _ in range(range_count):
                # parse and insert in each face
                parse_urls = {}
                time.sleep(7)
                search_list = driver.find_elements_by_class_name("member")
                #for search_index in range(len(actor_name_lists)):
                for tag in search_list:
                    try:
                        # search_save_text = tag.find_element_by_class_name('save-lead')
                        result = parse_sale_search(tag)
                        print('parsed result:', result)
                        update_sale_search(cur, owner_id, search_id, count, result)

                        # parse_urls[url] = 1
                        count += 1
                        if count >= limit:
                            break
                    except Exception as err:
                        print('err:', err)
                        continue

                    # get_search_contact_fast_with_salesurls(parse_urls, driver, cur, owner_id,
                    #                               search_id, count)

                if count >= limit:
                    break

                try:
                    driver.find_element_by_class_name(
                        "next-pagination .pagination-text").click()
                except Exception as err1:
                    print('No next:', err1)
                    count = limit + 1
                    break
            """

            get_search_contact_sale(parse_urls, driver, cur, owner_id, search_id,
                       parse_connection_link_sales)


            print('parsing profile:')
            for count, url in enumerate(parse_urls.keys()):
                result = parse_connection_link_sales(driver, url)
                # insert into data

                values = result + (owner_id, search_id,
                                   botstatus.CONNECT_REQ_N,)
                print('value insert:', values)
                add_to_db(cur, search_query, *values)
                print('count insert:', values)
                values = (count, search_id, )
                add_to_db2(cur, search_update_query, *values)
            """

            bot_status = botstatus.DONE
        # completed_date = datetime.now()
        # return name_list, company_list, title_list, location_list, bot_status, lastrun_date, completed_date

    except Exception as e:
        #bot_status = botstatus.ERROR
        bot_status = botstatus.DONE
        print("ERROR:", e)

    driver.close()

    completed_date = datetime.now()

    return bot_status, lastrun_date, completed_date


def parse_sale_search(tag):
    url_tag = tag.find_element_by_class_name(
        'name-link')
    url = url_tag.get_attribute('href')
    linked_uid = get_sale_nav_linkedid_id(url)
    name = url_tag.get_attribute('title')
    # compay
    company = ""
    try:
        company_tag = tag.find_element_by_class_name(
            'company-name')
        company = company_tag.get_attribute('title')
    except Exception as comperr:
        print('company:', comperr)
        pass

    # location
    location_tags = tag.find_elements_by_class_name(
        'info-value')

    title = ""
    location = ""
    try:
        title = get_contact_title(location_tags[0].text.strip())
        location  = location_tags[-1].text.strip()
    except Exception as locerr:
        print('location:', locerr)
        pass

    return (company, "", location, title, linked_uid, name)


def update_sale_search(cur, owner_id, search_id, count, result):
    values = result + (owner_id, search_id,
                           botstatus.CONNECT_REQ_N,)
    print('value insert:', values)
    # shorten title

    add_to_db2(cur, search_query, *values)

    values = (count + 1, search_id, )
    print('count insert:', values)
    add_to_db2(cur, search_update_query, *values)


def get_search_contact_sale(parse_urls, driver, cur, owner_id, search_id,
                       parse_func=parse_connection_link):

    print('parsing profile:', parse_urls)
    for count, url in enumerate(parse_urls.keys()):
        try:
            result = parse_func(driver, url)
        except:
            continue

        values = result + (owner_id, search_id,
                           botstatus.CONNECT_REQ_N,)
        print('value insert:', values)
        # shorten title

        add_to_db2(cur, search_query, *values)

        values = (count + 1, search_id, )
        print('count insert:', values)
        add_to_db2(cur, search_update_query, *values)


def get_search_contact(parse_urls, driver, cur, owner_id, search_id,
                       parse_func=parse_connection_link):
    print('get_search_contact parsing profile:', parse_urls)
    csrf_tocken = get_browser_csrf_tocken(driver)
    for count, url in enumerate(parse_urls.keys()):
        try:
            uid = url
            contact = get_contact_ajax(driver, uid, csrf_tocken)
            # ignore blank contact
            if contact['location'] == "" and contact['first_name'] == "":
                continue
            # values = (actor_company, industry, actor_location,
            #       actor_title, user_id, actor_name)
            name = "{first_name} {last_name}".format(**contact)
            result = (get_contact_title(contact['company']), contact['industry'],
                      contact['location'], get_contact_title(contact['title']),
                      uid, name,)
            values = result + (owner_id, search_id,
                           botstatus.CONNECT_REQ_N, contact['first_name'],
                           contact['last_name'], contact['countrycode'])
            print('value insert:', values)
            # shorten title
            add_to_db2(cur, search_query_v2, *values)
            values = (count + 1, search_id, )
            print('count insert:', values)
            add_to_db2(cur, search_update_query, *values)
        except Exception as err:
            print('error:', err, '------>')
            continue



def check_update_contact(driver, cur, owner_id):
    sql = """select id, linkedin_id from messenger_inbox where owner_id=%s"""
    cur.execute(sql, owner_id)
    csrf_tocken = get_browser_csrf_tocken(driver)
    starttime = time.time()
    for row in cur.fetchall():
        print('update row:', row)
        uid = row[1]
        contact = get_contact_ajax(driver, uid, csrf_tocken)

        values = (contact['location'], contact['industry'],
                  contact['countrycode'], contact['company'], contact['title'], row[0])
        add_to_db2(cur, inbox_update_query, *values)

    print('Done in ', (time.time() - starttime) , ' secs')


def verify_login(driver, pincode=None,
                 cur=None, owner_id=None, task_id=None, task_type=None):

    try:
        wait = WebDriverWait(driver, IDLE_INTERVAL_IN_SECONDS)
        # check if user is exist
        bot_status = botstatus.DONE
        if exist_user(wait):
            print("That user is an existing user.")
            if check_password_correct(wait):
                print('pw is correct')
                res = check_captcha(driver)
                if res == False:
                    return True

                # pin code verification
                res, no_pin_required = pinverify(
                    wait, pincode, cur, owner_id, task_id, task_type)
                if res and no_pin_required:
                    return True

                if (no_pin_required == False):
                    print("Pin to verify!")
                    if pincode is None:
                        bot_status = botstatus.PIN_REQUIRED
                    else:
                        bot_status = botstatus.PIN_INVALID
                else:
                    print("Successfully login without pin code verification!")

            else:
                print('password is wrong')
                bot_status = botstatus.ERROR

        else:
            print("That user is not exist in Linkedin.")
            bot_status = botstatus.ERROR
        return bot_status
    except Exception as e:
        bot_status = botstatus.ERROR
        print(bot_status, ':', e)
        driver.close()
        return bot_status


def auto_new_update():
    cur = botdb.get_cursor()
    ip = get_ip()
    get_linkedin_user = "SELECT * FROM app_linkedinuser WHERE bot_ip = '%s'"
    cur.execute(get_linkedin_user % ip)
    linked_users = cur.fetchall()
    if linked_users is None:
        print('--there is no user----->')
    for linked_user in linked_users:
        try:
            handle_new_contact(cur, linked_user[0])
            print('--->', linked_user)
        except Exception as e:
            print(e)
            continue
    print('number process user------>', len(linked_users))


def test_insert():
    sql = """INSERT INTO messenger_inbox (`company`, `industry`, `location`, `title`,
     `linkedin_id`, `name`, `latest_activity`,`status`, `is_connected`, `connected_date`,  `owner_id`)
     VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""
    v = ('MTI TECHNOLOGY Co., Ltd', '', 'Vietnam', 'Vice General Director',
         'yuji-tsuchiya-055b5828', 'Yuji Tsuchiya', '2018-05-10 12:42:36.857662',
         22, 1, '2018-05-10 12:42:36.857662', 35)

    # sql = sql % v
    print("sql:", sql)
    cur = get_cursor()
    cur.execute(sql, v)


def test_contact(url):
    cur = botdb.get_cursor()
    get_fastcontacts(user_email, user_pw, cur, 1)


def test_parse(url):
    driver = login_linkedin_withwebdriver(user_email, user_pw)
    return parse_connection_link(driver, url)


def test_search():

    cur = botdb.get_cursor()
    return search(user_email, user_pw, 'b2b', cur, 1, 1, )


def test_login():
    login_linkedin(user_email, user_pw)


def test_message():
    get_messages(user_email, user_pw, botdb.get_cursor())


def test_fastmessage():
    get_fastmessage(user_email, user_pw, botdb.get_cursor())


if __name__ == '__main__':
    print("Running.....")
    read_mysql()
    # auto_new_update()

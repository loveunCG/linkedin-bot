from datetime import datetime
import json
import time


from bot_driver import LINKEDIN_CONNECTIONS_URL
from bot_db import add_to_db2
import bot_db
from bot_driver import LINKEDIN_URL, get_browser_csrf_tocken
from bot_sql import getcontacts_query, inbox_check_id_query, inbox_update_query
import bottask_status as botstatus



def get_contact_title(actor_title):
    if len(actor_title) > 100:
        actor_title = actor_title[:99]
    return actor_title


def get_contact_ajax(driver, uid, csrf_tocken):
    url = """{0}/voyager/api/identity/profiles/{1}""".format(LINKEDIN_URL, uid)
    ele_id = 'interceptedResponse-%s' % uid
    js = """
      var element = document.createElement('div');
      element.id = "%s";
      element.appendChild(document.createTextNode(""));
      document.body.appendChild(element);
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          document.getElementById("%s").innerHTML = this.responseText;
        }
      };
      xhttp.open("GET", '""" + url + """', true);
      xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
      xhttp.send();
    """
    js = js % (ele_id, ele_id, )
    driver.execute_script(js)
    time.sleep(2)
    response_data = driver.find_element_by_id(ele_id).text

    return get_contact_data(response_data, uid)


def _get_contact_ajax(driver, uid, csrf_tocken):
    time.sleep(1)
    url = """{0}/voyager/api/identity/profiles/{1}""".format(LINKEDIN_URL, uid)
    csrf_tocken = csrf_tocken.replace('"', '')
    headers = {
        'Csrf-Token': csrf_tocken,
        'X-RestLi-Protocol-Version': '2.0.0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referer': 'https://linkedin.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'upgrade-insecure-requests': '1'
    }
    cookies = {'JSESSIONID': csrf_tocken}
    r = requests.get(url, cookies=cookies, headers=headers)
    print('response----->', r.text)
    return get_contact_data(r.text, uid)


def get_company_title(occupation):
    if ' at ' in occupation:
        parts = occupation.split(' at ')
    else:
        parts = ['', occupation]
    return parts[1], parts[0]


def get_contact_data(response_data, uid):
    data = dict(linked_id=uid, first_name="", last_name="",
                industry="", company="", title="",
                countrycode="", postalcode="", location="",
                )
    try:
        target_json_data = json.loads(response_data)
    except Exception as err:
        print('json error:', err, response_data)
        return data
    try:
        data['first_name'] = get_by_key(target_json_data, 'first_name')
        data['lastName'] = get_by_key(target_json_data, 'lastName')
        data['industry'] = get_by_key(target_json_data, 'industryName')
        occupation = get_by_key(target_json_data['miniProfile'], 'occupation')
        data['company'], data['title'] = get_company_title(occupation)
        data['location'] = get_by_key(target_json_data, 'locationName')
        basic_location = target_json_data['location']['basicLocation']
        data['countrycode'] = get_by_key(basic_location, 'countryCode')
        data['postalcode'] = get_by_key(basic_location, 'postalCode')
    except Exception as err:
        print('data error:', err)
    return data


def get_by_key(source, key):
    if key in source:
        return str(source[key]).replace("'", "")
    else:
        return ' '
    
    # this is wokring now but I have never any payment
    # this project will be down
    # that is fact


def get_fastcontact_ajax(driver, cur, owner_id, check_existed=False):
        
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
    time.sleep(100)
    targetjsondata = targetjsondata['elements']
    for itemdata in targetjsondata:
        firstName = itemdata['miniProfile']['firstName']
        lastName = itemdata['miniProfile']['lastName']
        occupation = itemdata['miniProfile']['occupation']
        publicIdentifier = itemdata['miniProfile']['publicIdentifier']
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
        actor_title = get_contact_title(actor_title)
        values = (actor_company, "", "", actor_title,
                  publicIdentifier, firstName + ' ' + lastName,)
        values = values + \
            (createdAtTime, str(botstatus.OLD_CONNECT_N),
             '1', createdAtTime, str(owner_id),)

        if check_existed:
            contact_row = bot_db.get_db(cur, inbox_check_id_query,
                                     (publicIdentifier, owner_id,))
            if contact_row is not None:
                continue

        if cur is not None:
            bot_db.add_to_db2(cur, getcontacts_query, *values)
            
            if check_existed:
                contact_row = bot_db.get_db(cur, inbox_check_id_query,
                                     (publicIdentifier, owner_id,))
                update_contact(driver, cur, publicIdentifier, csrf_tocken, contact_row[0])

    print(' Number of connections : ', len(targetjsondata))
    

def update_contact(driver, cur, uid, csrf_tocken, row_id):  
    contact = get_contact_ajax(driver, uid, csrf_tocken)

    values = (contact['location'], contact['industry'],
              contact['countrycode'], contact['company'], contact['title'], 
              row_id)
    
    add_to_db2(cur, inbox_update_query, *values)


def check_update_contact(driver, cur, owner_id):
    sql = """ select id, linkedin_id from messenger_inbox where owner_id=%s"""

    cur.execute(sql, owner_id)
    csrf_tocken = get_browser_csrf_tocken(driver)
    starttime = time.time()
    for row in cur.fetchall():
        print('update row:', row)
        uid = row[1]
        update_contact(driver, cur, uid, csrf_tocken, row[0])
    print('Done in ', (time.time() - starttime) , ' secs')

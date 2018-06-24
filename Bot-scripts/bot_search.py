# Fast Search
from datetime import datetime
import json
import time
import os

from bot_db import add_to_db2, add_to_db, get_cursor
from bot_driver import login_linkedin_withwebdriver, get_browser_csrf_tocken,\
    close_driver
from bot_sql import search_update_query, search_query
import bottask_status as botstatus
from bot_contact_detail import get_contact_title

def get_sale_nav_linkedid_id(url):
        # get user-id
        get_link = url.split("/")
        sales_user_url = get_link[5]
        sales_user_name = sales_user_url.split(",")
        user_id = sales_user_name[0] + ',' + sales_user_name[1]
        return user_id

def fast_search(email, password, search_data, cur=None, search_id=None,
                 owner_id=None, search_mode=0, limit=750):

    print('----------', search_data, '----------', search_mode)
    driver = login_linkedin_withwebdriver(email, password)
    max_count = limit
    total_count = 500
    lastrun_date = datetime.now()

    print("==== SEARCH ======")

    csrf_tocken = get_browser_csrf_tocken(driver)
    try:
        if search_mode == 0:
            time.sleep(5)
            js = """
              var element = document.createElement('div');
              element.id = "interceptedSearchResponse";
              element.appendChild(document.createTextNode(""));
              document.body.appendChild(element);
    
              var xhttp = new XMLHttpRequest();
    
              xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                  document.getElementById("interceptedSearchResponse").innerHTML = this.responseText;
                }
              };
              xhttp.open("GET", "https://www.linkedin.com/voyager/api/search/cluster?blendedSrpEnabled=true&count=""" + str(max_count) + """&guides=List()&keywords=""" + search_data + """&origin=GLOBAL_SEARCH_HEADER&q=guided&start=0", true);
              xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
              xhttp.send();"""
            #############################################################################################################################
            driver.execute_script(js)
            #############################################################################################################################
            time.sleep(3)
            searchListText = driver.find_element_by_id('interceptedSearchResponse').text
            jsondata = json.loads(searchListText)
            total_count = jsondata['paging']['total']
            print('total_count : ', total_count, searchListText.encode('utf-8'))
            close_driver(driver, email)
            return
            targetcount = max_count
            if max_count > total_count:
                targetcount = total_count

            targetcount = targetcount // 10 + 1

            for idx in range(targetcount):
                #############################################################################################################################
                driver.execute_script("""

                          var element = document.createElement('div');
                          element.id = "interceptedSearchResponse_""" + str(idx) + """";
                          element.appendChild(document.createTextNode(""));
                          document.body.appendChild(element);

                          var xhttp = new XMLHttpRequest();

                          xhttp.onreadystatechange = function() {
                            if (this.readyState == 4 && this.status == 200) {
                              document.getElementById("interceptedSearchResponse_""" + str(idx) + """").innerHTML = this.responseText;
                            }
                          };
                          xhttp.open("GET", "https://www.linkedin.com/voyager/api/search/cluster?blendedSrpEnabled=true&count=10&guides=List()&keywords=""" + search_data + """&origin=GLOBAL_SEARCH_HEADER&q=guided&start=""" + str(
                    idx * 10) + """", true);
                          xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                          xhttp.send();

                        """)
                #############################################################################################################################
            time.sleep(10)

            search_result_cnt = 0
            for idx in range(targetcount):
                conversationListText = driver.find_element_by_id('interceptedSearchResponse_' + str(idx)).text
                jsondata = json.loads(conversationListText)

                elementsData = jsondata['elements'][0]['elements']
                elementsCount = len(elementsData)

                for idx2 in range(elementsCount):
                    print(' ----------------------------------------')

                    profileData = elementsData[idx2]['hitInfo']['com.linkedin.voyager.search.SearchProfile']

                    txt_industry = ''
                    if 'industry' in profileData:
                        txt_industry = profileData['industry']
                    txt_location = ''
                    if 'location' in profileData:
                        txt_location = profileData['location']

                    txt_firstname = profileData['miniProfile']['firstName']
                    txt_lastname = profileData['miniProfile']['lastName']
                    txt_occupation = profileData['miniProfile']['occupation']
                    txt_linkedin_id = profileData['miniProfile']['publicIdentifier']

                    if txt_linkedin_id != 'UNKNOWN':

                        actor_title = ""
                        actor_company = ""
                        if " at " in txt_occupation:
                            title_company = txt_occupation.split(" at ")
                            actor_title = title_company[0]
                            actor_company = title_company[1]
                        else:
                            actor_company = ""
                            actor_title = txt_occupation

                        search_result_cnt += 1
                        values = (actor_company, txt_industry, txt_location, actor_title, txt_linkedin_id,
                                  txt_firstname + ' ' + txt_lastname)
                        get_search_contact_fast(values, cur, owner_id, search_id, search_result_cnt)

            bot_status = botstatus.DONE
        elif search_mode == 1:
            time.sleep(5)

            driver.get(search_data)
            print("-------Go to search url-----------")

            time.sleep(5)
            total_resultcounts_tag = driver.find_element_by_css_selector(
                "h3.search-results__total")
            total_resultcounts = total_resultcounts_tag.text
            result_counts = total_resultcounts.split(" ")
            real_counts = result_counts[1]
            counts = real_counts.replace(",", "")
            print('counts:', counts)

            targetcount = max_count
            if max_count > counts:
                targetcount = counts

            targetcount = targetcount // 10 + 1

            print('range_count:', targetcount)

            parse_urls = {}
            print('parsing url:')
            for _ in range(targetcount):
                time.sleep(3)
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(3)

                search_list = driver.find_elements_by_class_name(
                    "search-result__result-link")
                # print('search_list:', search_list)
                count = 0

                # for search_index in range(len(actor_name_lists)):

                for tag in search_list:
                    url = tag.get_attribute('href')
                    if url in parse_urls:
                        continue
                    parse_urls[url] = 1
                    count += 1
                    if count >= limit:
                        break

                try:
                    driver.find_element_by_class_name("next").click()
                except Exception as err1:
                    print('No next:', err1)
                    break

            get_search_contact_fast_with_urls(parse_urls, driver, cur, owner_id, search_id)
            """
            print('parsing profile:')
            for count, url in enumerate(parse_urls.keys()):
                result = parse_connection_link(driver, url)


                values = result + (owner_id, search_id,
                                   botstatus.CONNECT_REQ_N,)
                print('value insert:', values)
                add_to_db(cur, search_query, *values)
                print('count insert:', values)
                values = (count, search_id, )
                add_to_db2(cur, search_update_query, *values)

            """
            bot_status = botstatus.DONE
        else:
            time.sleep(2)
            driver.get(search_data)
            print("-------Go to sales navigator search url-----------")

            time.sleep(10)
            try:
                total_resultcounts_tag = driver.find_element_by_css_selector(
                    ".TR .spotlight-result-count")
            except:
                print("search has not result")
                values = (0, search_id,)
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
                values = (0, search_id,)
                add_to_db2(cur, search_update_query, *values)
                bot_status = botstatus.DONE
                driver.close()
                completed_date = datetime.now()
                return bot_status, lastrun_date, completed_date

            targetcount = max_count
            if max_count > real_counts:
                targetcount = real_counts
            
            
            targetcount = targetcount // 25 + 1

            print('range_count:', targetcount)

            

            print('parsing profile:')
            for _ in range(targetcount):
                parse_urls = {}
                time.sleep(7)
                
                search_list = driver.find_elements_by_class_name("member")

                # for search_index in range(len(actor_name_lists)):
                count = 0
                for tag in search_list:
                    try:
                        search_save_text = tag.find_element_by_class_name(
                            'save-lead')
                        url = tag.find_element_by_class_name(
                            'name-link').get_attribute('href')
                        if url in parse_urls:
                            continue
                        parse_urls[url] = 1
                        count += 1
                        if count >= limit:
                            break
                    except Exception as err:
                        continue
                    
                    get_search_contact_fast_with_salesurls(parse_urls, driver, 
                                                           cur, owner_id, 
                                                           search_id, count)

                try:
                    driver.find_element_by_class_name(
                        "next-pagination .pagination-text").click()
                except Exception as err1:
                    print('No next:', err1)
                    break

                

            """
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
        # bot_status = botstatus.ERROR
        bot_status = botstatus.DONE
        print("ERROR:", e)

    driver.close()

    completed_date = datetime.now()

    return bot_status, lastrun_date, completed_date


def get_search_contact_fast(profile_data, cur, owner_id, search_id, search_result_cnt):
    values = profile_data + (owner_id, search_id, botstatus.CONNECT_REQ_N,)
    print('value insert:', values)
    add_to_db(cur, search_query, *values)

    values = (search_result_cnt, search_id,)
    print('count insert:', values)
    add_to_db2(cur, search_update_query, *values)


def get_search_contact_fast_with_urls(parse_urls, driver, cur, owner_id, search_id):
    request_cookies_browser = driver.get_cookies()
    JSESSIONID = driver.get_cookie('JSESSIONID')
    csrf_tocken = JSESSIONID['value']

    print('parsing profile:', parse_urls)
    for count, url in enumerate(parse_urls.keys()):
        profileUrl = url.split('/')[-2]
        profileUrl = 'https://www.linkedin.com/voyager/api/identity/profiles/' + profileUrl + '/'

        #############################################################################################################################
        driver.execute_script("""
              var element = document.createElement('div');
              element.id = "interceptedProfile_""" + str(count) + """";
              element.appendChild(document.createTextNode(""));
              document.body.appendChild(element);

              var xhttp = new XMLHttpRequest();

              xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                  document.getElementById("interceptedProfile_""" + str(count) + """").innerHTML = this.responseText;
                }
              };
              xhttp.open('GET', '""" + profileUrl + """', true);
              xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
              xhttp.send();
                """)
        #############################################################################################################################
    time.sleep(5)

    for count, url in enumerate(parse_urls.keys()):
        print('============== count =========== :', count)
        profile_result = driver.find_element_by_id('interceptedProfile_' + str(count)).text
        jsonProfileData = json.loads(profile_result)

        txt_industry = jsonProfileData['industryName']
        txt_firstname = jsonProfileData['firstName']
        txt_lastname = jsonProfileData['lastName']
        txt_linkedin_id = url.split('/')[-2]
        txt_location = jsonProfileData['locationName']
        txt_occupation = jsonProfileData['headline']

        actor_title = ""
        actor_company = ""
        if " at " in txt_occupation:
            title_company = txt_occupation.split(" at ")
            actor_title = title_company[0]
            actor_company = title_company[1]
        else:
            actor_company = ""
            actor_title = txt_occupation

        values = (actor_company, txt_industry, txt_location, actor_title, txt_linkedin_id, txt_firstname + ' ' + txt_lastname)
        values = values + (owner_id, search_id, botstatus.CONNECT_REQ_N,)

        print('value insert:', values)
        add_to_db(cur, search_query, *values)

        values = (count + 1, search_id,)
        print('count insert:', values)
        add_to_db2(cur, search_update_query, *values)


def get_search_contact_fast_with_salesurls(parse_urls, driver, cur, owner_id, 
                                           search_id, counter):
    
    csrf_tocken = get_browser_csrf_tocken(driver)
    print('parsing profile:', parse_urls)
    for count, url in enumerate(parse_urls.keys()):
        try:

            milli_sec = int(round(time.time() * 1000))
            print('profile url:', url)
            profileUrl = url.split('?')[0] + '/pathfinder?_=' + str(milli_sec)
            
            divId = str(counter)
            js = """
                var element = document.createElement('div');
                element.id = 'interceptedSalesProfile_""" + divId + """';
                element.appendChild(document.createTextNode(""));
                document.body.appendChild(element);
                
                var xhttp = new XMLHttpRequest();
                
                xhttp.onreadystatechange = function() {
                  if (this.readyState == 4 && this.status == 200) {
                    document.getElementById('interceptedSalesProfile_""" + divId + """').innerHTML = this.responseText;
                  }
                };
                xhttp.open('GET', '""" + profileUrl + """', true);
                xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
                xhttp.send();
                """
            print('js:', js)
            
            #############################################################################################################################
            driver.execute_script(js)
            #############################################################################################################################
            time.sleep(2)
    
            
            print('============== count =========== :', count)
            
            profile_result = driver.find_element_by_id('interceptedSalesProfile_' + divId).text
            
            # if count == 0:
            print('profile_result:', profile_result)
                
    
            jsonProfileData = json.loads(profile_result)

            # get user-id
            get_link = url.split("/")
            sales_user_url = get_link[5]
            sales_user_name = sales_user_url.split(",")
            user_id = sales_user_name[0] + ',' + sales_user_name[1]

            txt_firstname = jsonProfileData['viewee']['firstName']
            txt_lastname = jsonProfileData['viewee']['lastName']
            txt_linkedin_id = user_id
            txt_location = jsonProfileData['viewee']['location']
            txt_occupation = jsonProfileData['viewee']['headline']
            txt_company = jsonProfileData['viewee']['company']


            actor_title = ""
            if " at " in txt_occupation:
                title_company = txt_occupation.split(" at ")
                actor_title = title_company[0]
            else:
                actor_title = txt_occupation

            actor_title = get_contact_title(actor_title)

            values = (txt_company, '', txt_location, actor_title, txt_linkedin_id, txt_firstname + ' ' + txt_lastname)
            values = values + (owner_id, search_id, botstatus.CONNECT_REQ_N,)

            print('value insert:', values)
            add_to_db2(cur, search_query, *values)
    
            values = (counter, search_id,)
            print('count insert:', values)
            add_to_db2(cur, search_update_query, *values)
        except Exception as err:
            print('error:', err)
            

def get_search_contact_salesurls(url, driver, cur=None, owner_id=None, 
                                           search_id=None, counter=1,
                                           request_cookies_browser=None):
    
    csrf_tocken = get_browser_csrf_tocken(driver)
    
    try:
            
        milli_sec = int(round(time.time() * 1000))
        print('profile url:', url)
        
        
        divId = str(counter)
        js = """
            var element = document.createElement('div');
            element.id = 'interceptedSalesProfile_""" + divId + """';
            element.appendChild(document.createTextNode(""));
            document.body.appendChild(element);
            
            var xhttp = new XMLHttpRequest();
            
            xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
            document.getElementById('interceptedSalesProfile_""" + divId + """').innerHTML = this.responseText;
            }
            };
            xhttp.open('GET', '""" + url + """', true);
            xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
            xhttp.setRequestHeader('cookie', '""" + request_cookies_browser + """')
            xhttp.send();
            """
        print('js:', js)
        
        #############################################################################################################################
        driver.execute_script(js)
        #############################################################################################################################
        time.sleep(2)

        
        print('============== count =========== :', counter)
        
        profile_result = driver.find_element_by_id('interceptedSalesProfile_' + divId).text
        
        # if count == 0:
        print('profile_result:', profile_result)
        
        return
        
        
        jsonProfileData = json.loads(profile_result)
    
    
    
        
        user_id  = get_sale_nav_linkedid_id(url)

        txt_firstname = jsonProfileData['viewee']['firstName']
        txt_lastname = jsonProfileData['viewee']['lastName']
        txt_linkedin_id = user_id
        txt_location = jsonProfileData['viewee']['location']
        txt_occupation = jsonProfileData['viewee']['headline']
        txt_company = jsonProfileData['viewee']['company']
        
        
        actor_title = ""
        if " at " in txt_occupation:
            title_company = txt_occupation.split(" at ")
            actor_title = title_company[0]
        else:
            actor_title = txt_occupation
            
        actor_title = get_contact_title(actor_title)
        
        values = (txt_company, '', txt_location, actor_title, txt_linkedin_id, txt_firstname + ' ' + txt_lastname)
        values = values + (owner_id, search_id, botstatus.CONNECT_REQ_N,)

        print('value insert:', values)
        
        if cur:
                
            add_to_db2(cur, search_query, *values)
    
            values = (counter, search_id,)
            print('count insert:', values)
            add_to_db2(cur, search_update_query, *values)
    except Exception as err:
        print('error:', err)
    
                        
def sale_nav_search(email, password, url, limit=1000):
    
    driver = login_linkedin_withwebdriver(email, password)
    max_count = limit
    
    print('url:', url)
    # url = url.replace('search?keywords', 'search/results?keywords')
    
    offset = 0
    mh = 100
    
    for i in range( limit // mh ):
        offset = mh * i
        pageurl = url + "&count={count}&start={start}".format(count=mh, start=offset)
        
        #get_search_contact_salesurls(pageurl, driver, None, None, None, i, cookies)
        driver.get(pageurl)
        time.sleep(5)
        """
        soup = BeautifulSoup(driver.page_source,  "html.parser")
        
        members = soup.find_all('li', class_='result')
        for member in members:
            # name and id_
            tag_a = member.find('a', class_='name-link')
            print( member)
            
            # info
        """
        
    driver.close()
    
        
user_email = os.environ.get('email', None)
user_pw = os.environ.get('pw', None)

if __name__ == '__main__':

    cur = get_cursor()
    """"
    values = ('Fabindia Overseas Pvt Ltd', '', 'Gurgaon, India', 
              "HeadOfDigital@Fabindia/ IMPACT 50MostInfluntialW'men", 
              '3377770,3-D0', 'Gauri Awasthi', 111, 50, 5)

    add_to_db2(cur, search_query, *values)
    """
    email = user_email
    password = user_pw
    search_data = "https://www.linkedin.com/sales/search?keywords=do%20less%20earn%20more&updateHistory=true&EL=auto&trk=d_sales2_nav_advancedsearch&trackingInfoJson.contextId=1496A604534F3715802CA711E62A0000"
    # cur = None
    search_id = 51
    owner_id = 111
    search_mode = 2
    limit = 1000
    sale_nav_search(email, password, search_data, 100)
    # fast_search(email, password, search_data, cur, search_id, owner_id, search_mode, limit)
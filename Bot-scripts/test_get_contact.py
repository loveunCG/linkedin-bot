import json
import os
import time

from bot import LINKEDIN_CONNECTIONS_URL
from bot_driver import get_driver, get_browser_csrf_tocken


def get_fastcontacts(email, password):
    
    driver = get_driver(email, password)
    print("==== GET CONTACTS ======")

    
    try:

        driver.get(LINKEDIN_CONNECTIONS_URL)
        time.sleep(10)

        total_connection_counts = driver.find_element_by_tag_name("h2")
        counts_text = total_connection_counts.text
        counts = counts_text.split(" ")

        cnt_all_connections = counts[0].replace(',', '')
        csrf_tocken = get_browser_csrf_tocken(driver)
        url = "https://www.linkedin.com/voyager/api/relationships/connections?count=" + cnt_all_connections
        url = url + "&sortType=RECENTLY_ADDED&start=0"        
        url = url + "&projection=(elements*(to~(id,localizedFirstName,localizedLastName)))"
        
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
          xhttp.open("GET", '""" + url + """', true);
          xhttp.setRequestHeader('Csrf-Token', """ + csrf_tocken + """)
          xhttp.send();""")
        #############################################################################################################################
        time.sleep(3)
        responsedata = driver.find_element_by_id('interceptedResponse').text

        #print('responsedata :', responsedata)
        targetjsondata = json.loads(responsedata)
        print('----------------targetjsondata------------------> :', targetjsondata)
        
    except Exception as err:
        print('errors:', err)
        
    driver.close()
    
        
        
email = os.environ.get('email')
password = os.environ.get('pw')
if __name__ == '__main__':
    start = time.time()
    
    rows = get_fastcontacts(email, password)
    done = time.time() - start
    
    print('done in:', done, ' secs')
    
    print('rows::', "\n\n")
    for i, row in enumerate(rows):
        print(i+1, ':::', row)
    
    
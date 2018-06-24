import requests
from bot_db import get_cursor, add_to_db2


# table = 'app_freebotip'
check_query = "SELECT id FROM app_linkedinuser WHERE bot_ip=%s"
check_query2 = "SELECT id FROM app_freebotip WHERE bot_ip=%s"

insert_query = """INSERT INTO app_freebotip (`bot_ip`) VALUES(%s)"""

SERVER_IP = None

def get_ip():
    global SERVER_IP
    if SERVER_IP:
        return SERVER_IP

    res = requests.get('http://ip.42.pl/raw')
    ip = res.text.strip()
    SERVER_IP = ip
    print('ip:', ip)
    return ip

def get_db_row(cur, sql, *values):
    cur.execute(sql, values)
    return cur.fetchone()
    
def check_bot_ip(cur, ip):
    
    row = get_db_row(cur, check_query, ip)
    
    if row is None:
        print('{0} ip is not used in linkedinUser table'.format(ip))
        row = get_db_row(cur, check_query2, ip)
    return row


def check_and_add_ip(cur=None):
    if cur is None:
        cur = get_cursor()
        
    ip = get_ip()
    
    row = check_bot_ip(cur, ip)
    if row is None:
        print('{0} ip is not in app_freebotip table'.format(ip))
        add_to_db2(cur, insert_query, ip)
        
    
import os
import datetime
import pymysql
from db_config import DB_HOST, DB_PW, DB_USER, DB_NAME

insert_contacts_query = "INSERT INTO messenger_inbox (`company`, `industry`, `location`, `title`, `linkedin_id`, `name`, `latest_activity`,`status`, `is_connected`, `connected_date`, `owner_id`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"

login_query = "SELECT email, password FROM app_linkedinuser WHERE id=%s"

contact_select = """select id, linkedin_id from messenger_inbox where linkedin_id = '%s' and owner_id=%s"""
message_select = """SELECT id FROM messenger_chatmessage WHERE (time BETWEEN '%s' AND '%s') and contact_id=%s and owner_id=%s and is_direct=%s and is_read=%s and is_sent=%s"""


def get_user_email_pw(cur, owner_id):
    sql = login_query % owner_id
    print('sql:', sql)
    cur.execute(sql)
    result = cur.fetchone()
    email = result[0]
    password = result[1]
    return email, password


def add_to_db(cur, getcontacts_query, *values):
    # may check record exists
    sql = getcontacts_query % values
    print('sql:', sql)
    # print('add to db:', insert_contacts_query, values)
    try:
        cur.execute(sql)
    except Exception as err:
        print('Insert inbox error:', err)


def add_to_db2(cur, getcontacts_query, *values):
    # may check record exists
    sql = getcontacts_query % values
    # print('sql:', sql)
    # print('add to db:', insert_contacts_query, values)
    try:
        cur.execute(getcontacts_query, values)
    except Exception as err:
        print('Insert inbox error:', err)
        add_to_db(cur, getcontacts_query, *values)


def update_or_insert_contact(cur, getcontacts_query, *values):
    select_sql = contact_select % (values[4], values[10])
    cur.execute(select_sql)
    result = cur.fetchone()
    if result is None:
        sql = insert_contacts_query % values
        print('sql:', sql)
    else:
        return False
    try:
        cur.execute(sql)
        select_sql = contact_select % (values[4], values[10])
        cur.execute(select_sql)
        result = cur.fetchone()
        print('insert-------->', result)
        return result
    except Exception as err:
        print('Insert inbox error:', err)
        return False


def remove_trim(value):
    return str(value).replace("'", "")


def update_or_insert_message(cur, getmessage_query, *values):
    start_date, end_date = get_start_end_time(values[3])
    select_sql = message_select % (start_date, end_date, values[5], values[6], values[7], values[8], values[9])
    print('sql:', select_sql)
    try:
        cur.execute(select_sql)
        result = cur.fetchone()
    except Exception as e:
        print(e)
        return False
    if result is None:
        sql = getmessage_query % (values[0], values[1], remove_trim(values[2]), values[3], values[4], values[5], values[6], values[7], values[8], values[9])
        print('sql:', sql)
    else:
        return False
    try:
        cur.execute(sql)
        return True
    except Exception as err:
        print('Insert inbox error:', err)
        return False


def get_start_end_time(message_time):
    # message_time = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S.%f")
    print(message_time)
    print(message_time.year, message_time.month, message_time.day, message_time.hour, message_time.minute,)
    start_time = datetime.datetime(message_time.year, message_time.month, message_time.day, message_time.hour, message_time.minute, 0, 000000)
    end_time = start_time + datetime.timedelta(minutes=1)
    print(start_time, end_time)
    return start_time, end_time


def get_db(cur, sql, values):
    print(sql % values)
    cur.execute(sql, *values)
    return cur.fetchone()


def get_cursor():
    db_user = os.environ.get('dbuser', DB_USER)
    db_pw = os.environ.get('dbpw', DB_PW)
    db_host = os.environ.get('dbhost', DB_HOST)
    db_name = os.environ.get('dbname', DB_NAME)
    # previous_rows_count = 0
    connect = None
    try:
        connect = pymysql.connect(
            host=db_host, user=db_user, password=db_pw, db=db_name, autocommit=True)
    except Exception as err:
        print("Could not open database:", err)
        exit(-1)
    connect.set_charset(('utf8mb4'))
    cur = connect.cursor()
    return cur


if __name__ == '__main__':
    print("Running.....")

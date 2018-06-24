import os


from bot import get_fastmessage
from bot_driver import login_linkedin_withwebdriver
from bot_db import get_cursor

user_email = os.environ.get('email', None)
user_pw = os.environ.get('pw', None)

def test_message():
    
    driver = login_linkedin_withwebdriver(user_email, user_pw)
    #time.sleep(10)
    get_fastmessage(user_email, user_pw, get_cursor(), 77, driver)
    


if __name__ == '__main__':
    print("Running.....")
    
    test_message()
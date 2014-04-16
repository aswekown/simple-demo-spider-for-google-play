# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import sqlite3
import sys

# connect the sqlite3 

def Conn_DB(db_name = 'app_info.db'):
  try:
    conn = sqlite3.connect(db_name)
  except Exception, e:
    print "Conn Error ", e
  return conn

# get the category of the apps

def Get_Category(root_address):
  url_list = root_address.split('/')
  return url_list[-1].replace("?",' ').split(' ')[0]

# we have to login so that to get the info from every app

def Login_Google(browser, category_root_address):
  
  browser.get(category_root_address)

  # click to login
  login_link = browser.find_element_by_id('gb_70')
  webdriver.ActionChains(browser).move_to_element(login_link).click(login_link).perform()

  # input your email here
  email = browser.find_element_by_name('Email')
  # you should input your email here
  email.send_keys('') 

  # input your password here
  pwd = browser.find_element_by_name('Passwd')
  # you should input your password for your email here
  pwd.send_keys('')
  pwd.send_keys(Keys.RETURN)

  print 'Login Success'


# load the whole page and then return the number of the apps under the category

def Load_All_Apps(browser):

  # try to load the whole page to select want I want, the magic number 13 is based on the test
  
  for times in xrange(13):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2.5)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
    sleep(2.5)
    print times

    # click the show more button to load more apps
    show_more_button = browser.execute_script("return document.querySelector('#show-more-button')['style']['cssText'];")
    if show_more_button != 'display: none;':
      browser.execute_script("document.querySelector('#show-more-button').click();")
      print 'click button'
    print show_more_button

  # to the bottom of the page
  browser.execute_script("window.scrollTo(0, 0);")

  number = browser.execute_script("return document.querySelectorAll('button.price').length;")
  print number
  
  return number

def Click_Install_Button(browser, category_root_address):
  get_permissions_code = """var permissions = document.querySelectorAll('.perm-description');
var precise_locaton = 'precise location (GPS and network-based)';
var approximate_location = 'approximate location (network-based)';
var ways = '';

for (var perm in permissions) {
	if (permissions[perm].innerHTML == precise_locaton) {
		ways += 'p';
	} else if (permissions[perm].innerHTML == approximate_location) {
		ways += 'a';
	}
}
return ways;"""

  # get all install button objects
  get_button_list_code = """return document.querySelectorAll('button.price');"""
  button_list = browser.execute_script(get_button_list_code)
  # print dir(button_list[0])
  # button_list.reverse()

  numbers_of_button = len(button_list)

  count = 0
  # index = 1
  sleep(3)

  #webdriver.ActionChains(browser).move_to_element(button_list[1]).click(button_list[1]).perform()
  #sleep(1)
  #browser.execute_script("document.querySelector('#purchase-cancel-button').click();")
  #webdriver.ActionChains(browser).move_to_element(button_list[3]).click(button_list[3]).perform()
  #sleep(1)
  #browser.execute_script("document.querySelector('#purchase-cancel-button').click();")
  
  category = Get_Category(category_root_address)

  get_app_address_code = """var app_address_list = document.querySelectorAll("h2 a");var list = [];
for (var i = 0; i < app_address_list.length; i++) {list.push(app_address_list[i]['href']);} return list;"""
  address_list = browser.execute_script(get_app_address_code)

  conndb = Conn_DB()
  db_cursor = conndb.cursor()

  number_of_i_want = 0

  insert_sql = u"""insert into app_info (categroy, name, link, get_geo_ways) values ('{0}', '{1}', '{2}', '{3}')"""

  for index in range(1, numbers_of_button, 2):
    try:
      webdriver.ActionChains(browser).move_to_element(button_list[index]).click(button_list[index]).perform()
      sleep(3.5)
      count += 1
      #index += 2
    except IndexError:
      print "Out of index"
      break
    
    try:
      print "Count ", count
      perms = browser.execute_script(get_permissions_code)
      sleep(2)
      appname = browser.execute_script("return document.querySelector('.purchase-header .title').innerHTML;")
      print u"App id is: ", appname , u"Perm is: ", perms, u"Address is: ", address_list[count - 1]
      
      if perms:
        sql_with_data = insert_sql.format(category, appname, address_list[count - 1], perms)
        db_cursor.execute(sql_with_data)
        conndb.commit()
        number_of_i_want += 1
        
    except Exception, e:
      print "Error for ", e, "Number is ", count, "Pers is", perms
      continue
    # click cancle button
    browser.execute_script("document.querySelector('#purchase-cancel-button').click();")
    sleep(1)

  print "compary ", count , numbers_of_button, "I want :", number_of_i_want
  db_cursor.close()
  conndb.close()
  # print browser.execute_script()

if __name__ == '__main__':
  root_address = 'https://play.google.com/store/apps/category/TRAVEL_AND_LOCAL?hl=en'
  
  driver = webdriver.Chrome()
  Login_Google(driver, root_address)
  Load_All_Apps(driver)
  Click_Install_Button(driver, root_address)

  #sys.exit()

  fd = file("./res.txt", "wb")
  fd.write("over")
  fd.close()

  

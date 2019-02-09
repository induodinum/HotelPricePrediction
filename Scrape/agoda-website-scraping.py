# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# ไฟล์ต้นเเบบ ดึงเเค่หน้าเดียว
# comment / uncomment : ctrl + 1

################### import library & set some variable #####################
from selenium import webdriver # act like a web browser
from bs4 import BeautifulSoup # extract information from 
import time # slow down the algorithm
import re
scroll_pause_time,last_height,first_height,element_index,hotel_id = [1,0,0,0,0]
divided_scroll_height = 25  #change number of scroll time here
data_vary = dict(hotel_id = [],rating = []) # just cre8 your own hotel id
data_static = dict(hotel_id = [],hotel_name = [],location = [],star = [],hotel_property_highlight = [])
hotel_property_highlights = ''
############################################################################

############################## access website ##############################
chrome_driver_path_com9 = r'C:\Users\5842005226\Desktop\chromedriver.exe'
chrome_driver_path_home = r'C:\Users\Paem\Desktop\chromedriver.exe'
driver = webdriver.Chrome(chrome_driver_path_com9)
agoda_link = 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=pQHcFhcOgT1iFOHcHh9CK0AXliAn3pVicobeM5oOB5Lpu%2FkHTZ8bidJkAafXyw%2BeGqKI1BOaN53Vz0if59rn3T0uwvDnXtRrCnxah1kRfQRbbLljNIoQWvnNa%2BGTWIWlY72HwZahr%2Fz%2F2J35oVOD7%2BAhjORQmn7mEovVTalPNyKFlb511A%2B6K5RCv7rBtlZZbS3dzzacn%2Bn7QZeTArmFD8PSDzITsjmxLRNaEuNpzeA%3D&city=9395&cid=1646637&tick=636851292319&languageId=1&userId=4f5832b5-d4c3-4f4e-b879-07304220c449&sessionId=2ka41itnuneusez04jfatgxi&pageTypeId=1&origin=TH&locale=en-US&tag=b2961ddc-64cb-d9fc-b99e-6ce3addebc66&gclid=CjwKCAiAqOriBRAfEiwAEb9oXbWodr9IaNfD47h2QaYWb2uOo6ErLgqIXO-F1HLOn4jJrGCuUCYd-hoCbocQAvD_BwE&aid=82361&currencyCode=USD&htmlLanguage=en-us&cultureInfoName=en-US&ckuid=4f5832b5-d4c3-4f4e-b879-07304220c449&prid=0&checkIn=2019-02-16&checkOut=2019-02-17&rooms=1&adults=2&children=0&priceCur=USD&los=1&textToSearch=Bangkok&travellerType=1&productType=-1&sort=agodaRecommended'
driver.get(agoda_link)
############################################################################

######## scroll the webpage, click at each hotel and scrape the data #######
agoda_page_height = driver.execute_script("return document.body.scrollHeight") # get the original page height
click_elements = driver.find_elements_by_xpath('//h3[@class="hotel-name"]') # get the original click element
scroll_height = agoda_page_height/divided_scroll_height
while True:
    last_height += scroll_height
    driver.execute_script("window.scrollTo(" + str(first_height) + ", " + str(last_height) + ")")
    first_height = last_height
    click_elements_new = driver.find_elements_by_xpath('//h3[@class="hotel-name"]')
    agoda_new_page_height = driver.execute_script("return document.body.scrollHeight")
    if len(click_elements_new) > len(click_elements):
        click_elements = click_elements_new
    if last_height > click_elements[element_index].location['y']:
        click_elements[element_index].click() # click the element
        driver.implicitly_wait(15) # browser wait for 5 second
        driver.switch_to_window(driver.window_handles[1]) # switch to next window
        each_hotel_raw_html = driver.execute_script("return document.documentElement.outerHTML") # scrape the data
        # cre8 the function to extract the room detail
        ## collect static data ##
        soup = BeautifulSoup(each_hotel_raw_html,'lxml')
        hotel_name = soup.find('h1',{'class':"FirstTileContent__Title"}).get_text()
        hotel_location = soup.find('div',{'class':"FirstTileContent__Address"}).get_text()
        hotel_star_string = soup.find('i',{'data-selenium':"mosaic-hotel-rating"})['class'][3]
        hotel_star = int(re.findall('.*-([0-9]*)',hotel_star_string)[0])
        hotel_star = hotel_star/10 if hotel_star > 5 else hotel_star # correct the star
        hotel_property_highlights_list = soup.find_all('li',{'class':"fav-features__listitem fav-features__listitem__4 qa-fav-features__listitem"})
        for hotel_property_highlight in hotel_property_highlights_list:
            hotel_property_highlight_text = hotel_property_highlight.find('p',{'class':"fav-features__text fav-features__text--small"}).get_text()
            hotel_property_highlights += hotel_property_highlight_text + ';'
        ## collect vary data ##
        hotel_user_rating = float(soup.find('span',{'class':'ReviewScore-Number'}).get_text())
        hotel_recommended_by_percent_of_user = int(soup.find('div',{'class':"ReviewRecommendationCompact__Text"}).strong.get_text())
        
        ## collect all room type ##
        hotel_all_room_type_info = soup.find('div',{'class':'RoomGrid-content'}).contents
        for hotel_room_type_info in hotel_all_room_type_info:
            hotel_id = hotel_room_type_info['id'] # use in feature finding function
            hotel_room_type_span = hotel_room_type_info.find('span',{'data-selenium':'masterroom-title-name'})
            if hotel_room_type_span is not None: # check whether hotel_room_type obj is not 1) recommend tab or 2) sold out
                hotel_room_type_name = hotel_room_type_span.get_text() # get room type text
                hotel_room_type_info_prices_benefits = hotel_room_type_info.find('div',{'class':'ChildRoomsList'}).contents # get all prices & bentfit in each hotel_room_type 
                for hotel_room_type_info_price_benefit in hotel_room_type_info_prices_benefits:
                    hotel_room_type_benefits = hotel_room_type_info_price_benefit.find('div',{'class':"ChildRoomsList-room-featurebucket ChildRoomsList-room-featurebucket-Benefits"}).contents # find all benefits
                    hotel_room_type_price = hotel_room_type_info_price_benefit.find('div',{'class':'PriceContainer'})# find the price
                    if hotel_room_type_benefits is not None and hotel_room_type_price is not None: # if benefits & price avaiable -> finds all benefits and price
                        hotel_room_benefits = ''
                        for hotel_room_type_each_benefit in hotel_room_type_benefits[1:]: #find all benefits except 'benefit' head column
                            hotel_room_benefits += hotel_room_type_each_benefit.find('span',{'class':"ChildRoomsList-roomFeature-TitleWrapper"}).get_text() + ';'
                        hotel_room_price = int(hotel_room_type_price.find('div',{'class':'finalPrice'}).find('strong',{'data-ppapi':"room-price"}).get_text()) # extract room price
                        hotel_room_price_currency = hotel_room_type_price.find('div',{'class':'finalPrice'}).find('span',{'class':"pd-currency"}).get_text() # extract currency
                    # เก็บข้อมูลทั้งหมดใน for loop นี้
                # cre8 the function that extract the room info
                #  - click the feature button
                #  - soup = BeautiSoup
                #  - extract the feature
                #  - if unclickable error occur -> avoid it and do nothing
                #  - click the exit button
                
        
        
        driver.switch_to_window(driver.window_handles[0]) # switch to main window
        #################### close unused tab ####################
        default_handle = driver.current_window_handle 
        handles = list(driver.window_handles)  
        assert len(handles) > 1
        handles.remove(default_handle)
        assert len(handles) > 0
        driver.switch_to_window(handles[0])
        driver.close()
        driver.switch_to_window(default_handle) 
        ##########################################################
        element_index += 1 # += 1 at clement index
    if agoda_new_page_height - agoda_page_height > 100:
        scroll_height = (agoda_new_page_height - agoda_page_height)/divided_scroll_height
        agoda_page_height = agoda_new_page_height
    elif agoda_new_page_height - agoda_page_height < 100 and agoda_new_page_height - agoda_page_height > 1:
        scroll_height = agoda_new_page_height - agoda_page_height
        agoda_page_height = agoda_new_page_height
    else:
        pass
    if abs(agoda_page_height - last_height) < 1:
        break # actually, find the next_page button and click on it (if last page : break)
    time.sleep(scroll_pause_time)
############################################################################    
    
####################### extract the html #############################        
all_click_elements = driver.find_elements_by_xpath('//h3[@class="hotel-name"]')
for element in all_click_elements:
    element.click()
    
completed_raw_html = driver.execute_script("return document.documentElement.outerHTML")
soup = BeautifulSoup(completed_raw_html,'lxml')
driver.quit()
######################################################################


## TEST CODE ##
from selenium import webdriver
from bs4 import BeautifulSoup
import time
chrome_driver_path_com9 = r'/Users/pudit/Downloads/chromedriver'
chrome_driver_path_home = r'C:\Users\Paem\Desktop\chromedriver.exe'
driver = webdriver.Chrome(chrome_driver_path_com9)
agoda_link = 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=9395&checkIn=2019-02-16&los=1&rooms=1&adults=2&children=0&cid=-218&languageId=1&userId=4f5832b5-d4c3-4f4e-b879-07304220c449&sessionId=qxbkxohvb22ukr5a0jkjuaac&pageTypeId=1&origin=TH&locale=en-US&aid=130589&currencyCode=USD&htmlLanguage=en-us&cultureInfoName=en-US&ckuid=4f5832b5-d4c3-4f4e-b879-07304220c449&prid=0&checkOut=2019-02-17&priceCur=USD&textToSearch=Bangkok&productType=-1&travellerType=1'
driver.get(agoda_link)
#completed_raw_html = driver.execute_script("return document.documentElement.outerHTML")
#soup = BeautifulSoup(completed_raw_html,'lxml')

main_page = driver.current_window_handle # get the main page location
driver.find_element_by_xpath('//h3[@class="hotel-name"]').click() # click the button

driver.current_window_handle
driver.window_handles
driver.switch_to_window(driver.window_handles[1])

completed_raw_html = driver.execute_script("return document.documentElement.outerHTML")
soup = BeautifulSoup(completed_raw_html,'lxml')

################ close unused tab after scraping ###################
default_handle = driver.current_window_handle
handles = list(driver.window_handles)
assert len(handles) > 1
handles.remove(default_handle)
assert len(handles) > 0
driver.switch_to_window(handles[0])
# do your stuffs
driver.close()
driver.switch_to_window(default_handle)
######################################################################

def sliding_window(): # sliding window until find the element
    return None
    
def find_hotel_feature(driver,hotel_id):
    element_path = '//*[@id="' + hotel_id + '"]/div[1]/div[1]/a/div/div[1]/span'
    driver.find_element_by_xpath(element_path).click() # apply click on the element
    time.sleep(2)
    completed_raw_html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(completed_raw_html,'lxml')
    all_pop_up_element = soup.find_all('div',{'class':'ReactModalPortal'})
    index = 0
    while True:
        pop_up_element_consider = all_pop_up_element[index]
        if pop_up_element_consider.find('div',{'class':'details__info-area'}) is not None:
            # extract all feature in string
            return None
    

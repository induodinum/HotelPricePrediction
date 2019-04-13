from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import time # slow down the algorithm
import re
import datetime
import random
import os

def clear_list():
    Hotel_name = []
    Hotel_roomtype = []
    Hotel_prices = []
    Hotel_prices_standard = []
    Hotel_benefits = []
    Time_collect = []
    
    return Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect


# In[3]:


def delete_list(Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect):
    del Hotel_name
    del Hotel_roomtype
    del Hotel_prices
    del Hotel_prices_standard
    del Hotel_benefits
    del Time_collect


# In[4]:


def scroll_page_till_find(scroll_pause_time,last_height,scroll_height,element,driver):
    while True:
        first_height = last_height
        last_height += scroll_height
        driver.execute_script("window.scrollTo(" + str(first_height) + ", " + str(last_height) + ")")
        first_height = last_height
        time.sleep(scroll_pause_time)
        if abs(last_height - element.location['y']) <= scroll_height*3:
            break
    return last_height


# In[5]:


def close_unused_tab(driver, default_window_handle): # close the tab that is located on right side of the main tab
    handles = list(driver.window_handles)  
    assert len(handles) > 1
    handles.remove(default_window_handle)
    assert len(handles) > 0
    driver.switch_to_window(handles[0])
    driver.close()
    driver.switch_to_window(default_window_handle)


# In[6]:


def save_to_pkl(count, datapath, d):
    t_date = datetime.datetime.now()
    today = t_date.isoformat()[:10]
    i = 1

    while(i):
        filename = "{}hotel_price_{}_{}.pkl".format(datapath, today, i)
        exists = os.path.isfile(filename)
        if exists:
            i += 1
        else:
            filehandler = open(filename, 'wb')
            print(filename)
            break

    pickle.dump(d,filehandler)
    filehandler.close()


# In[7]:


#load data
import pickle
import os

def get_data_static(datapath):
    path_data_static = '{}data_static_21_13.pickle'.format(datapath)
    data_static = pickle.load(open(path_data_static,'rb'))
    
    return data_static


# In[66]:


def get_webdriver():
    chrome_driver_path_com9 = r'C:\Users\5842005226\Desktop\chromedriver.exe'
    home_indy_path = r'E:\Downloads\Programs\chromedriver_win32\chromedriver.exe'
    mac_indy_path = '/Users/Indy/Downloads/chromedriver'

    driver = webdriver.Chrome(home_indy_path)  # choose one path

    # change the link here
    agoda_link = 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=9395&checkIn=2019-04-20&los=1&rooms=1&adults=2&children=0&cid=-1&languageId=1&userId=7deafcf4-77d1-43a5-92b9-dd8f64158191&sessionId=jrdsi52uxzlsvmsjfidmyzar&pageTypeId=1&origin=TH&locale=en-US&aid=130243&currencyCode=THB&htmlLanguage=en-us&cultureInfoName=en-US&ckuid=7deafcf4-77d1-43a5-92b9-dd8f64158191&prid=0&checkOut=2019-04-21&priceCur=THB&textToSearch=Bangkok&travellerType=1&familyMode=off&productType=1&hotelStarRating=5,4,3,2,1&sort=reviewAll'
    driver.get(agoda_link)

    try:
        driver.maximize_window()
    except WebDriverException:
        pass
    
    return driver


# In[9]:


def scroll_to_the_end_of_page(driver):
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True


# In[10]:


def find_next_btn(driver):
    return driver.find_element_by_xpath('//div[@class="clearfix pagination-panel"]/div/button[@id="paginationNext"]')


# In[30]:


def click_next_page(driver,n,m=random.randint(22,30)):   # n is the number of clicks, m is the number of arrow up's
    if(n!=0):
        for i in range(n):
            scroll_to_the_end_of_page(driver)
            time.sleep(2)

            actions = ActionChains(driver)

            for i in range(m):
                actions.send_keys(Keys.ARROW_UP)
            actions.perform()

            time.sleep(3)
            try:
                next_btn = find_next_btn(driver)
                next_btn.click()
            except:
                continue
            time.sleep(3)
        
    return n

def get_scraped_data(each_hotel_raw_html, data_static, hotel_all_info, prices_length):
    # Hotel_name = hotel_all_info[0]
    # Hotel_roomtype = hotel_all_info[1]
    # Hotel_prices = hotel_all_info[2]
    # Hotel_prices_standard = hotel_all_info[3]
    # Hotel_benefits = hotel_all_info[4]
    # Time_collect = hotel_all_info[5]

    soup = BeautifulSoup(each_hotel_raw_html,'lxml')
    try:
        hotel_name = soup.find('h1',{'class':"FirstTileContent__Title"}).get_text()
        hotel_all_room_type_info = soup.find('div',{'id':"property-room-grid-root"}).find('div',{'class':'RoomGrid-content'})
        try:
            if hotel_name in data_static['hotel_name'] and hotel_all_room_type_info.div['class'][0] != 'RoomGrid-searchTimeOut':# check whether 'all' hotel room is sold out or not
                for hotel_room_type_info in hotel_all_room_type_info.contents: # 'all' room not sold out -> collect the data
                    hotel_room_type_span = hotel_room_type_info.find('span',{'data-selenium':'masterroom-title-name'})
                    if hotel_room_type_span is not None: # check whether hotel_room_type obj is normal or not
                        hotel_room_type_name = hotel_room_type_span.get_text()
                        hotel_room_type_info_prices_benefits = hotel_room_type_info.find('div',{'class':'ChildRoomsList'}).contents # get all prices & bentfit in each hotel_room_type 
                        for hotel_room_type_info_price_benefit in hotel_room_type_info_prices_benefits[1:]:
                            hotel_room_benefits = ''
                            hotel_room_type_price = hotel_room_type_info_price_benefit.find('div',{'class':'PriceContainer'})# find the price
                            hotel_room_type_benefits = hotel_room_type_info_price_benefit.find('div',{'class':"ChildRoomsList-room-featurebucket ChildRoomsList-room-featurebucket-Benefits"}).contents # find all benefits
                            for hotel_room_type_each_benefit in hotel_room_type_benefits[1:]: #find all benefits except 'benefit' head column
                                hotel_room_benefits += hotel_room_type_each_benefit.find('span',{'class':"ChildRoomsList-roomFeature-TitleWrapper"}).get_text() + ';'
                            hotel_room_price_str = hotel_room_type_price.find('div',{'class':'finalPrice'}).find('strong',{'data-ppapi':"room-price"}).get_text() # extract room price
                            hotel_room_price_int = int(''.join(hotel_room_price_str.split(',')))
                            if hotel_room_type_price.find('div',{'class':"CrossedOutPrice "}) is None:
                                hotel_room_price_standard = hotel_room_price_int
                            else:
                                hotel_room_price_standard = float(hotel_room_type_price.find('div',{'class':"CrossedOutPrice "})["data-element-cor"])
                            hotel_all_info[0].append(hotel_name)
                            hotel_all_info[1].append(hotel_room_type_name)
                            hotel_all_info[2].append(hotel_room_price_int)
                            hotel_all_info[3].append(hotel_room_price_standard)
                            hotel_all_info[4].append(hotel_room_benefits)
                            hotel_all_info[5].append(datetime.datetime.now())

                            prices_length += 1
                            print('prices_length ++')
                    else:
                        pass
            else:
                pass
        except TypeError:
            pass
    except AttributeError: # if the page is not normal -> just close it
        pass

    return hotel_all_info, prices_length
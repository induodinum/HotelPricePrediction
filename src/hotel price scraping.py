
# coding: utf-8

# In[70]:


from selenium import webdriver # act like a web browser
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementNotVisibleException # import unclickable exception
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup # extract information from 

import time # slow down the algorithm
import re
import datetime
import random

from multiprocessing import Process, JoinableQueue, Value
from functools import partial

scroll_height = 200


# In[2]:


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
    
    filehandler = open("{}hotel_price_{}_.pkl".format(datapath, today),"wb")
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
    agoda_link = 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=9395&languageId=1&userId=f999c86a-637d-4fd0-b64a-694a50ff2af9&sessionId=pslwacfdrebdevmetq4zbbyp&pageTypeId=103&origin=TH&locale=en-US&cid=-1&aid=130243&currencyCode=THB&htmlLanguage=en-us&cultureInfoName=en-US&ckuid=f999c86a-637d-4fd0-b64a-694a50ff2af9&prid=0&checkIn=2019-04-20&checkOut=2019-04-21&rooms=1&adults=2&children=0&priceCur=THB&los=1&textToSearch=Bangkok&travellerType=1&familyMode=off&productType=1&hotelStarRating=5,4,3,2,1&sort=reviewAll'
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


def click_next_page(driver,n,m=random.randint(16,22)):   # n is the number of clicks, m is the number of arrow up's
    if(n!=0):
        for i in range(n):
            scroll_to_the_end_of_page(driver)
            time.sleep(2)

            actions = ActionChains(driver)

            for i in range(m):
                actions.send_keys(Keys.ARROW_UP)
            actions.perform()

            time.sleep(3)
            next_btn = find_next_btn(driver)
            next_btn.click()
            time.sleep(3)
        
    return n


# In[71]:


def scrape_hotel_data(n_page_clicked):
    print('-3')
#     driver = *args[0]
#     data_static = *args[1]
#     page_clicked = *args[2]
#     driver, data_static, page_clicked

    datapath = 'C:/Users/Indy/Desktop/coding/HotelPricePrediction/data/'
    driver = get_webdriver()
    data_static = get_data_static(datapath)
    next_page_clicked = n_page_clicked.value
    
    print('-2')
    page_clicked = click_next_page(driver, next_page_clicked)
    next_page_clicked += page_clicked
    
    print('-1')
    n_page_clicked.value = next_page_clicked

    Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect = clear_list()
    file_count = 0
    prices_length = 0
    next_page_clicked = 0
    prices_memory_limit = 10000

    # Start scraping

    try:
        driver.maximize_window()
    except WebDriverException:
        pass
    continue_scrape = False ## if continue scrape <- change this to TRUE
    print('0')
    for it in range(2):
        print('1')
        if not continue_scrape:
            default_window_handle = driver.current_window_handle
            #hotel_id_in_our_database = 0
            last_height = 0
            element_index = 0
            click_elements = driver.find_elements_by_xpath('//h3[@class="hotel-name"]') # get the original click element
        for it2 in range(5):
            print('2')
            last_height = scroll_page_till_find(1.2,last_height,scroll_height,click_elements[element_index],driver)
            time.sleep(0.5) # wait for the data to be loaded
            click_elements_new = driver.find_elements_by_xpath('//h3[@class="hotel-name"]') # get the loaded data
            if len(click_elements_new) > len(click_elements): # if new data loaded -> update the data
                click_elements = click_elements_new # update the data
            try: # try to click the element
                click_elements[element_index].click() # click the element
            except WebDriverException: # if cannot -> close the popup
                try:
                    print('found popup')
                    popup_close = driver.find_element_by_xpath('//div[@class="LeaveSitePopup-CloseArea"]/span')
                    popup_close.click() # close the popup

                    # click somewhere else which isn't a popup
                    print('closed popup')

                except NoSuchElementException:
                    try:
                        somewhere_area = driver.find_element_by_xpath('//div[@class="Filter__Container"]')
                        actions = ActionChains(driver)
                        actions.move_to_element_with_offset(somewhere_area,0,0)
                        actions.click()
                        actions.perform()
                        print('close popup')
                        time.sleep(0.5)

                    except:
                        actions = ActionChains(driver)
                        actions.move_by_offset(200,-40)
                        actions.click()
                        actions.perform()
                        print('no such element')
                        time.sleep(0.5)

                click_elements_2 = driver.find_elements_by_xpath('//h3[@class="hotel-name"]')
                click_elements_2[element_index].click() # click the element again
            time.sleep(1) # browser wait
            driver.switch_to_window(driver.window_handles[1]) # switch to next window
            time.sleep(9)
            each_hotel_raw_html = driver.execute_script("return document.documentElement.outerHTML") # scrape the data
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
                                    Hotel_name.append(hotel_name)
                                    Hotel_roomtype.append(hotel_room_type_name)
                                    Hotel_prices.append(hotel_room_price_int)
                                    Hotel_prices_standard.append(hotel_room_price_standard)
                                    Hotel_benefits.append(hotel_room_benefits)
                                    Time_collect.append(datetime.datetime.now())

                                    prices_length += 1
                            else:
                                pass
                    else:
                        pass
                except TypeError:
                    pass
            except AttributeError: # if the page is not normal -> just close it
                pass

            driver.switch_to_window(default_window_handle)
            close_unused_tab(driver, default_window_handle)

            if(prices_length>=prices_memory_limit):
                prices_length = 0

                file_count += 1
                print(file_count)

                d = {'Hotel_name':Hotel_name,
                'Hotel_roomtype':Hotel_roomtype,
                'Hotel_prices':Hotel_prices,
                'Hotel_prices_standard':Hotel_prices_standard,
                'Hotel_benefits':Hotel_benefits,
                'Time_collect':Time_collect}

                save_to_pkl(file_count, datapath, d)
                delete_list(Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect)
                Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect = clear_list()

            element_index += 1
            if element_index >= len(click_elements): # if scroll down till find the last element -> break
                continue_scrape = False
                break

        try: # try to click the next-page button
            next_element = driver.find_element_by_xpath('//div[@class="clearfix pagination-panel"]/div/button[@id="paginationNext"]') # เสือกกด previous
            scroll_page_till_find(1.1,last_height,scroll_height,next_element,driver)
            #break
            next_element.click()
            next_page_clicked += 1
            print('next page clicked', next_page_clicked)
            time.sleep(5)
        except WebDriverException:
            break
            
    # n_page_clicked.value = next_page_clicked


# In[78]:


if __name__=='__main__':
    next_page_clicked = 1
    times = 1
    tenmin = 10
    
    # q = JoinableQueue()
    n_page_clicked = Value('i', 0)
        
    for i in range(times):
        
        p = Process(target=scrape_hotel_data, args=(n_page_clicked,))
        p.start()
        print('-4')
               
        p.join()
        print('stopped process')

    print(n_page_clicked.value)

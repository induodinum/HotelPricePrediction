
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

from my_scraping_methods import clear_list, delete_list, scroll_page_till_find, close_unused_tab
from my_scraping_methods import save_to_pkl, get_data_static, get_webdriver, click_next_page, get_scraped_data

scroll_height = 300

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
    prices_memory_limit = 1000

    # Start scraping

    P = 2
    H = 10000

    for it in range(P):     # P = number of pages to scrape
        print('0')
        continue_scrape = False   ## if continue scrape <- change this to TRUE
        try:
            driver.maximize_window()
        except WebDriverException:
            pass
        time.sleep(2)

        print('1')

        if not continue_scrape:
            default_window_handle = driver.current_window_handle
            #hotel_id_in_our_database = 0
            last_height = 0
            element_index = 0
            click_elements = driver.find_elements_by_xpath('//h3[@class="hotel-name"]') # get the original click element
        for it2 in range(H):    # H = number of hotels to scrape
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
                    time.sleep(3)
                    actions = ActionChains(driver)
                    actions.move_by_offset(-500,-300)
                    actions.click()
                    actions.perform()
                    print('no such element')
                    time.sleep(0.5)
                except:
                    try:
                        print('found popup')
                        popup_close = driver.find_element_by_xpath('//div[@class="LeaveSitePopup-CloseArea"]/span')
                        popup_close.click() # close the popup

                        # click somewhere else which isn't a popup
                        print('closed popup')
                    except NoSuchElementException:
                        somewhere_area = driver.find_element_by_xpath('//div[@class="Filter__Container"]')
                        actions = ActionChains(driver)
                        actions.move_to_element_with_offset(somewhere_area,0,0)
                        actions.click()
                        actions.perform()
                        print('close popup')
                        time.sleep(0.5)

                        try:
                            print('dunno what to do')
                        except:
                            pass

                click_elements_2 = driver.find_elements_by_xpath('//h3[@class="hotel-name"]')
                click_elements_2[element_index].click() # click the element again

            time.sleep(1) # browser wait
            driver.switch_to_window(driver.window_handles[1]) # switch to next window
            time.sleep(9)
            each_hotel_raw_html = driver.execute_script("return document.documentElement.outerHTML") # scrape the data
            
            hotel_all_info = [Hotel_name, Hotel_roomtype, Hotel_prices, Hotel_prices_standard, Hotel_benefits, Time_collect]
            hotel_all_info = get_scraped_data(each_hotel_raw_html, data_static, hotel_all_info, prices_length)

            driver.switch_to_window(default_window_handle)
            close_unused_tab(driver, default_window_handle)

            if(prices_length>=prices_memory_limit):
                prices_length = 0

                file_count += 1
                print(file_count)

                d = {
                'Hotel_name':hotel_all_info[0],
                'Hotel_roomtype':hotel_all_info[1],
                'Hotel_prices':hotel_all_info[2],
                'Hotel_prices_standard':hotel_all_info[3],
                'Hotel_benefits':hotel_all_info[4],
                'Time_collect':hotel_all_info[5],
                }


                save_to_pkl(file_count, datapath, d)
                delete_list(Hotel_name, Hotel_roomtype, Hotel_prices,  Hotel_prices_standard, Hotel_benefits, Time_collect)
                del hotel_all_info
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
            
    n_page_clicked.value = next_page_clicked
    print('next page to click: ', n_page_clicked.value)

# In[78]:


if __name__=='__main__':
    next_page_clicked = 1
    times = 1000
    tenmin = 10
    
    # q = JoinableQueue()
    n_page_clicked = Value('i', 0)
        
    for i in range(times):
        print('n_page_c before', n_page_clicked.value)

        p = Process(target=scrape_hotel_data, args=(n_page_clicked,))
        p.start()
        print('-4')
        
        p.join()
        print('stopped process')

        n_page_clicked.value += 1
        print('n_page_c after', n_page_clicked.value)
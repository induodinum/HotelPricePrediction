
# coding: utf-8

# In[10]:


import numpy as np
import pandas as pd
import pickle

from os import listdir, walk
from os.path import isfile, join


# In[16]:


datapath = 'C:/Users/Indy/Desktop/coding/HotelPricePrediction/data/'
path_hotel_data = datapath + 'hotel_data.xlsx'
path_hotel_room_data = datapath + 'hotel_room_data.xlsx'

date = '2019-04-13'
path_hotel_day_11 = [f for f in listdir(datapath) if 'hotel_price_{}'.format(date) in f]


# In[13]:


df_day_11 = pd.DataFrame()

for path in path_hotel_day_11:
    pkl_11 = pickle.load(open(datapath + path, 'rb'))
    df_i = pd.DataFrame(pkl_11)
    
    df_day_11 = df_day_11.append(df_i)
    
df_day_11 = df_day_11.reset_index(drop=True)
print(df_day_11.shape)


# In[14]:


df_day_11


# In[37]:


# do the inner join
hotel_data = pd.read_excel(path_hotel_data)
hotel_room_data = pd.read_excel(path_hotel_room_data)
hotel_price = df_day_11.copy()

del hotel_price['Hotel_prices_standard']


# In[20]:


merged_data = pd.merge(hotel_data,hotel_room_data,how='inner',on='hotel_id_in_our_database')
count_null = merged_data.isna().sum()
count_null[count_null != 0]


# In[23]:


hotel_price.describe().loc[:, 'Hotel_prices']


# In[44]:


hotel_price.head()


# # Rename columns

# In[50]:


hotel_price = hotel_price.rename(columns={'Hotel_name': 'hotel_name', 
                                          'Hotel_roomtype': 'hotel_room_type', 
                                          'Hotel_benefits': 'hotel_benefits', 
                                          'Hotel_prices': 'hotel_price'})

hotel_room_data = hotel_room_data.rename(columns={'hotel_room_Type_Names': 'hotel_room_type'})


# In[51]:


print('hotel_data shape : ' + str(hotel_data.shape))
print('hotel_room_data shape : ' + str(hotel_room_data.shape))
print('hotel_price shape : ' + str(hotel_price.shape))


# ถ้าห้องโรงเเรมที่เก็บมาใน 1 วันซ้ำกัน -> drop ห้องโรงเเรมทิ้งให้เหลือห้องเดียว

# In[52]:


hotel_data.head()


# In[53]:


hotel_room_data.head()


# found the null data
# - drop data in room_capacity
# - keep the null value in view

# # Merge hotel data with room data

# In[54]:


merged_data = merged_data.dropna(subset=['Room Capacity','hotel_star'])
merged_data.loc[:,['view']] = merged_data.loc[:,['view']].fillna('unknown')
count_null = merged_data.isna().sum()
count_null[count_null != 0]


# do the inner join with the hotel_price column -> use hotel_name + room_type_name + room_benefit as keys

# however.....

# # Drop duplicated data

# In[55]:


database_id = merged_data['hotel_name'] + merged_data['hotel_room_Type_Names'] + merged_data['hotel_room_Benefits']
merged_data['hash'] = database_id.apply(hash)
duplicated_mask = merged_data.duplicated(subset = 'hash',keep=False)
merged_data[duplicated_mask]


# We've found the duplicate row in hotel database (which it shouldn't be)

# So, we keep only one row, and remove all duplicate rows

# In[56]:


# get all duplicate index
duplicated_mask = merged_data.duplicated(subset = 'hash',keep='first')
drop_list = list(merged_data[duplicated_mask].index)
merged_data.drop(drop_list,inplace = True)
duplicated_mask = merged_data.duplicated(subset = 'hash',keep=False)
merged_data[duplicated_mask]


# In[57]:


print('merged_data shape : ' + str(merged_data.shape))


# Now we not found the duplicated rows in hotel database -> we're good to go

# In[58]:


hotel_price.columns


# In[60]:


hotel_price['hotel_benefits']


# # Merge hotel data with price data

# In[65]:


merged_data = merged_data.rename(columns={'hotel_room_Type_Names': 'hotel_room_type'})
merged_data


# In[66]:


## do the left join with the hotel_price column -> use hotel_name + room_type_name + number of benefit + benefits as keys
# count benefits
merged_data_benefits = merged_data['hotel_room_Benefits'].str.split(';')
hotel_price_benefits = hotel_price['hotel_benefits'].str.split(';')
# add in data
merged_data['number_benefits'] = merged_data_benefits.apply(len)
hotel_price['number_benefits'] = hotel_price_benefits.apply(len)
merged_data_n = pd.merge(merged_data,hotel_price,how='inner',on=['hotel_name','hotel_room_type','number_benefits']) # join the data


# In[69]:


list(merged_data_n.columns)


# In[71]:


# derive benefit column
free_wifi_mask = merged_data_n['hotel_room_Benefits'].str.contains('Free Wi-Fi') == merged_data_n['hotel_benefits'].str.contains('Free Wi-Fi')
free_breakfast_mask = merged_data_n['hotel_room_Benefits'].str.contains('Free breakfast') == merged_data_n['hotel_benefits'].str.contains('Free breakfast')
cancel_policy_mask = merged_data_n['hotel_room_Benefits'].str.contains('Cancellation policy') == merged_data_n['hotel_benefits'].str.contains('Cancellation policy')
free_cancel_mask = merged_data_n['hotel_room_Benefits'].str.contains('Free cancellation') == merged_data_n['hotel_benefits'].str.contains('Free cancellation')
pay_nothing_mask = merged_data_n['hotel_room_Benefits'].str.contains('Pay nothing until') == merged_data_n['hotel_benefits'].str.contains('Pay nothing until')
extra_low_price_mask = merged_data_n['hotel_room_Benefits'].str.contains('Extra low price') == merged_data_n['hotel_benefits'].str.contains('Extra low price')
pay_at_hotel_mask = merged_data_n['hotel_room_Benefits'].str.contains('Pay at hotel') == merged_data_n['hotel_benefits'].str.contains('Pay at hotel')
without_credit_card_mask = merged_data_n['hotel_room_Benefits'].str.contains('Book without credit card') == merged_data_n['hotel_benefits'].str.contains('Book without credit card')
airport_mask = merged_data_n['hotel_room_Benefits'].str.contains('Airport') == merged_data_n['hotel_benefits'].str.contains('Airport')
express_mask = merged_data_n['hotel_room_Benefits'].str.contains('Express') == merged_data_n['hotel_benefits'].str.contains('Express')
selected_mask = free_wifi_mask & free_breakfast_mask & cancel_policy_mask & free_cancel_mask & pay_nothing_mask & extra_low_price_mask & pay_at_hotel_mask & without_credit_card_mask & airport_mask & express_mask
merged_data_n = merged_data_n[selected_mask]
del merged_data_n['hotel_benefits']
# cre8 benefit columns
b = merged_data_n['hotel_room_Benefits'].str.contains('Free Wi-Fi')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_free_wifi'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Free breakfast')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_free_breakfast'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Cancellation policy')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_cancel_policy'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Free cancellation')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_free_cancellation'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Pay nothing until')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_pay_nothing'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Extra low price')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_low_price'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Pay at hotel')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_pay_at_hotel'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Book without credit card')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_book_without_card'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Airport')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_airport'] = a
b = merged_data_n['hotel_room_Benefits'].str.contains('Express')
a = np.zeros(merged_data_n.shape[0])
a[b] = 1
merged_data_n['benefit_express'] = a


# In[72]:


# check null value after inner join data
count_null = merged_data_n.isna().sum()
count_null[count_null != 0]


# In[73]:


# check merged data shape
merged_data_n.shape


# In[74]:


del merged_data_n['number_benefits']
del merged_data_n['hash']


# In[124]:


merged_data = merged_data_n.copy()


# after join -> null value on Time_collect column column -> fuck it & good to go

# Next, include some variable
#  - จำนวนวันที่เก็บล่วงหน้า
#  - เขตโรงแรม
#  - 

# In[125]:


list(merged_data.columns)


# In[126]:


# cre8 new variable
## note : check in date = 20/4/2019 & check out date = 21/4/2019
import datetime

############### if use days_before_checin : use this ########################
# # extract num date before checkin
# f = lambda x: x.date().day
# merged_data['days_before_checkin'] = 20 - merged_data['Time_collect'].apply(f)
#############################################################

############### if use group by price -> use this #########################
# group by hash and find the ค่ากลางของ price (let says mean)
new_price = merged_data[['hotel_name','hotel_price','hotel_room_type', 'benefit_free_wifi', 'benefit_free_breakfast', 'benefit_cancel_policy', 'benefit_free_cancellation', 'benefit_pay_nothing',
 'benefit_low_price', 'benefit_pay_at_hotel', 'benefit_book_without_card', 'benefit_airport', 'benefit_express']].groupby(by = ['hotel_name','hotel_room_type', 'benefit_free_wifi', 'benefit_free_breakfast', 'benefit_cancel_policy', 'benefit_free_cancellation', 'benefit_pay_nothing',
 'benefit_low_price', 'benefit_pay_at_hotel', 'benefit_book_without_card', 'benefit_airport', 'benefit_express'],as_index=False).mean()
# del merged_data['hotel_price'] # since got the price
del merged_data['Time_collect'] # since time doesnt matter
#remove duplicate variable
duplicated_mask = merged_data.duplicated(subset = ['hotel_name','hotel_room_type', 'benefit_free_wifi', 'benefit_free_breakfast', 'benefit_cancel_policy', 'benefit_free_cancellation', 'benefit_pay_nothing',
 'benefit_low_price', 'benefit_pay_at_hotel', 'benefit_book_without_card', 'benefit_airport', 'benefit_express'],keep='first')
drop_list = list(merged_data[duplicated_mask].index)
merged_data.drop(drop_list,inplace = True)
#############################################################


# In[127]:


# find the district

merged_data['district'] = merged_data['hotel_location'].str.extract('(.*), Bangkok')
merged_data['district'] = merged_data['district'].apply(lambda x: x.split(',')[-1])
merged_data['district'] = merged_data['district'].apply(lambda x: x.strip(' '))
# cre8 dummy for view variable
merged_data = pd.get_dummies(merged_data,columns = ['view','district'])
#del merged_data['view_unknown'],merged_data['distinct_ Sukhumvit'] # avoid dummy trap (if use regression)


# In[128]:


merged_data.shape


# In[129]:


list(merged_data.columns)


# In[131]:


# export data
merged_data.to_csv(datapath + 'hotel_predict_data.csv')


# In[132]:


list(merged_data.describe().columns)


# **Tune max_depth & learning rate**

# import data (shortcut)

# In[133]:


import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import re

path_hotel_price = datapath + 'hotel_predict_data.csv'
merged_data = pd.read_csv(path_hotel_price)
X_col = list(merged_data.describe().columns)
X_col = list(set(X_col) - {'hotel_price'})

regex = re.compile(r"\[|\]|<", re.IGNORECASE)
X = merged_data[X_col]
Y = merged_data['hotel_price']
X.columns = [regex.sub("_", col) if any(x in str(col) for x in set(('[', ']', '<'))) else col for col in X.columns.values]
X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.1,random_state = 1)


# In[ ]:


# cre8 the model
merged_data = pd.merge(merged_data,new_price,how='inner',on=['hotel_name','hotel_room_type', 'benefit_free_wifi', 'benefit_free_breakfast', 'benefit_cancel_policy', 'benefit_free_cancellation', 'benefit_pay_nothing',
 'benefit_low_price', 'benefit_pay_at_hotel', 'benefit_book_without_card', 'benefit_airport', 'benefit_express']) # inner join new Y

# merged_data['district_ Klongtoey'][merged_data['district_ Klong Toey'].notnull()] += 1
# del merged_data['district_ Klong Toey']

X_col = list(merged_data.describe().columns)
X_col = list(set(X_col) - {'hotel_price'})
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import re
regex = re.compile(r"\[|\]|<", re.IGNORECASE)
X = merged_data[X_col]
Y = merged_data['hotel_price']
X.columns = [regex.sub("_", col) if any(x in str(col) for x in set(('[', ']', '<'))) else col for col in X.columns.values]
X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.1)
acc_valid = []
acc_std = []
for n_estimator in range(5,800,5):
  model = xgb.XGBRegressor(n_estimators = n_estimator)
  scores = cross_val_score(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
  acc_valid.append(np.mean(scores))
  acc_std.append(np.std(scores))
import matplotlib.pyplot as plt
plt.plot(range(5,800,5),acc_valid,'g-')
plt.plot(range(5,800,5),np.array(acc_valid) + 1.96*np.array(acc_std),'g--')
plt.plot(range(5,800,5),np.array(acc_valid) - 1.96*np.array(acc_std),'g--')
plt.title('Overfit plot for n_estimators parameter for xgboost')
plt.xlabel('n_estimators')
plt.ylabel('negative mean absolute error')
plt.axvline(x=795,color = 'blue')
plt.show()


# In[ ]:


acc_valid[150:]


# choose n_estimators = 795

# since we didnt determine learning_rate -> fuck it

# **Tune max_depth**

# In[ ]:


acc_valid = []
acc_std = []
for max_depth in range(1,15):
  model = xgb.XGBRegressor(n_estimators = 795,max_depth = max_depth)
  scores = cross_val_score(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
  acc_valid.append(np.mean(scores))
  acc_std.append(np.std(scores))
import matplotlib.pyplot as plt
plt.plot(range(1,15),acc_valid,'g-')
plt.plot(range(1,15),np.array(acc_valid) + 1.96*np.array(acc_std),'g--')
plt.plot(range(1,15),np.array(acc_valid) - 1.96*np.array(acc_std),'g--')
plt.title('Overfit plot for max_depth parameter for xgboost')
plt.xlabel('max_depth')
plt.ylabel('mean absolute error')
plt.axvline(x=6)
plt.show()


# In[ ]:


acc_valid


# In[ ]:


acc_std


# choose max_depth = 6

# **tune the rest of parameter**

# Train Gamma
# - if error in train set & test set lying too close -> lower gamma
# - if train set & test set differs too much -> model too complex without control -> higher gamma
# - if train cv not increase or increase too slowly -> lower gamma (since the value is too high)
# ref : https://medium.com/data-design/xgboost-hi-im-gamma-what-can-i-do-for-you-and-the-tuning-of-regularization-a42ea17e6ab6

# In[ ]:


# find the train cv and test cv
from sklearn.model_selection import cross_validate
model = xgb.XGBRegressor(n_estimators = 795,max_depth = 6)
cv = cross_validate(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
print('training set avg score : ' + str(np.mean(cv['train_score'])))
print('testing set avg score : ' + str(np.mean(cv['test_score'])))


# since train cv and test cv is too far -> use higher gamma

# In[ ]:


# try to use gamma = 200
from sklearn.model_selection import cross_validate
model = xgb.XGBRegressor(n_estimators = 795,max_depth = 6,gamma = 200)
cv = cross_validate(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
print('training set avg score : ' + str(np.mean(cv['train_score'])))
print('testing set avg score : ' + str(np.mean(cv['test_score'])))


# In[ ]:


# try to use gamma = 50
from sklearn.model_selection import cross_validate
model = xgb.XGBRegressor(n_estimators = 795,max_depth = 6,gamma = 60)
cv = cross_validate(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
print('training set avg score : ' + str(np.mean(cv['train_score'])))
print('testing set avg score : ' + str(np.mean(cv['test_score'])))


# worse -> try to use gamma < 1

# In[ ]:


# try to use gamma = 0.05
from sklearn.model_selection import cross_validate
model = xgb.XGBRegressor(n_estimators = 795,max_depth = 6,gamma = 0.05)
cv = cross_validate(model,X_train,Y_train,scoring = 'neg_mean_absolute_error',cv = 10)
print('training set avg score : ' + str(np.mean(cv['train_score'])))
print('testing set avg score : ' + str(np.mean(cv['test_score'])))


# since error is better -> consider low gamma
# 
# gamma = [0,0.0001,0.0004,0.001,0.004,0.01,0.04,0.1,0.4,1,4,10,40]

# also
# 
# colsample_bytree = [0.5,0.6,0.7,0.8,0.9,1]
# 
# subsample = [0.5,0.6,0.7,0.8,0.9,1]

# In[ ]:


from sklearn.model_selection import RandomizedSearchCV
param_test1 = {'min_child_weight':[1,3,5,7,9],'colsample_bytree':[0.5,0.6,0.7,0.8,0.9,1.0],'subsample':[0.5,0.6,0.7,0.8,0.9,1.0],'gamma':[0,0.0001,0.0004,0.001,0.004,0.01,0.04,0.1,0.4,1]}
rsearch1 = RandomizedSearchCV(estimator = xgb.XGBClassifier(n_estimators=795, max_depth=6), param_distributions = param_test1, scoring='neg_mean_absolute_error', cv=10,n_jobs=-1)
rsearch1.fit(X_train,Y_train)
rsearch1.best_params_, rsearch1.best_score_


# In[ ]:


model = xgb.XGBRegressor(n_estimators = 795,max_depth = 6)
model.fit(X_train,Y_train)
Y_pred = model.predict(X_test)
mape_all = 100*abs(Y_pred - Y_test)/Y_test
mae_all = abs(Y_pred - Y_test)
mape = np.mean(mape_all)
mae = np.mean(mae_all)


# In[ ]:


print('mape for XGBoost = ' + str(mape))
print('mae for XGBoost = ' + str(mae))


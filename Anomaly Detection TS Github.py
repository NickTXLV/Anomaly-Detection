# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 16:04:22 2021

@author: dodso
"""
# Import Packages
import pandas as pd
import numpy as np
import requests as r
import io

#Get Data by scrapping the dataset from my GitHub
#Outlier Data
res =r.get('https://raw.githubusercontent.com/NickTXLV/Anomaly-Detection/main/OutlierData.csv')

res.status_code

df = pd.read_csv(io.StringIO(res.text))

#Holiday Data
res_holiday=r.get('https://raw.githubusercontent.com/NickTXLV/Anomaly-Detection/main/HolidayTable.csv')

holiday = pd.read_csv(io.StringIO(res_holiday.text))


#Under structure of file, especially missing data
df.describe()
df.dtypes
df.shape
print('########## Missing Data #########')
print(df.isna().sum())

#Prepare Data for Analysis

#Fill Missing Chain ID with Independent
df[['Parent Store ID']]= df[['Parent Store ID']].fillna(value='No P ID')

#Format Datetime to Date
df['Date']=pd.to_datetime(df['Date']).dt.date

#Sort Data by Customer/Date
df.sort_values(by=['Store Number','Date'],inplace=True)

#Set Index as Date
#df.set_index('Date',drop=True,inplace=True).format

#Drop Unnecessary Columns
df.drop(['Forecast Mechanism','POS', 'Year_Day'],axis=1, inplace=True)

#Filter to only Cashmere Sweaters
one_sku = df[df['Sweater-Type']=='Cashmere']

#Create Features for Data
#Day
one_sku['day_name'] = pd.DatetimeIndex(one_sku['Date']).day_name()
#weekday
one_sku['weekday'] = pd.DatetimeIndex(one_sku['Date']).weekday
#Weekday
one_sku['is_weekday'] = np.select(
    [
     one_sku['weekday'].between(0,4,inclusive=True)
     ],
    ['1'
     ],
    default='0')
#Weekend
one_sku['is_weekend'] = np.select(
    [
     one_sku['weekday'].between(5,6, inclusive=True)
     ],
    [
     '1'
     ],
    default='0')

#Flag Holiday's
holiday['Date']=pd.to_datetime(holiday['Date']).dt.date
#Left join holiday df to one_sku
final_sku=one_sku.merge(holiday,how='left',on='Date')
#fill NA with 0
final_sku[['Flag']] = final_sku[['Flag']].fillna(value='0')
#rename ty to is_holiday
final_sku.rename(columns= {'Flag' : 'is_holiday'},inplace=True)


#Create Moving Averages
#Simple 10 Day moving Avergae by Customer 
final_sku['10_Day_MA'] = final_sku.groupby(['Store Number']).rolling(10)['Forecast Units'].mean().reset_index(drop=True)
#Simple Prior 2 Day moving Average by Customer/Day Name 
final_sku['2Day_MA_Customer/Day']=final_sku.groupby(['Store Number','day_name'])['Forecast Units'].transform(lambda x: x.rolling(2, 2).mean())


#Define Outlier
#Flag as an outlier if Forecast Units is >=50% of the 10 Day Moving Average
final_sku['10_Day_MA Outlier']=np.select(
    [
     ((final_sku['Forecast Units']-final_sku['10_Day_MA'])/final_sku['10_Day_MA'])>=.5,
     ],
     ['1'],
     default='0').astype(str).astype(int)



#2 Flag as an outlier if Forecast Units is >=50% of the 2_Day_MA-Day/Customer Average
final_sku['2_Day_MA-Day/Customer_Outlier']=np.select(
    [
     ((final_sku['Forecast Units']-final_sku['2Day_MA_Customer/Day'])/final_sku['2Day_MA_Customer/Day'])>=.5,
     ],
     ['1'],
     default='0').astype(str).astype(int)

#Count Outliers

final_sku['Outlier']=final_sku['10_Day_MA Outlier']+final_sku['2_Day_MA-Day/Customer_Outlier']

#rename Forecast Units columns to ForecastUnits so I can filter on it. The space
#was throwing an error

final_sku.rename(columns= {'Forecast Units' : 'ForecastUnits'},inplace=True)

Anomaly_Results= final_sku[(final_sku.Outlier==2) & (final_sku.is_holiday!=1) & (final_sku.ForecastUnits>=10)]

#Print('### Results of Analysis###')
print('### Results of Analysis ###')
print('This script found' , len(Anomaly_Results), 'Anomalies.')
print('These Anomalies represent' , format((len(Anomaly_Results)/len(df)*100),'.2f')+'%',
      'of the overall data set.')













# 









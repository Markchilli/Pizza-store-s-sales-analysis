#!/usr/bin/env python
# coding: utf-8

# In[76]:


import os # to improve performance, reduce overhead, 
# and enhance flexibility in the context of cloud computing and virtualization.
import warnings # to issue and catch warnings 
# that occur when certain conditions or unexpected situations arise.
warnings.filterwarnings('ignore') # in this case to ignore the warnings. 

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
from scipy import stats
from matplotlib.ticker import FuncFormatter

import calendar
from datetime import datetime as dt


# # 1. Dataset Cleansing

# In[77]:


df = pd.read_csv('C:/Users/Acer/Downloads/Personal project - Pizza store Analysis.csv')
df


# In[78]:


#Check for the data types
df.info()


# In[79]:


#Change the data type of TransactionDate into date
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], format = '%Y-%m-%d')
df.info()


# In[80]:


new_df = df.drop('Unnamed: 0', axis = 1)
new_df


# In[81]:


new_df.shape


# In[82]:


new_df.describe(include = 'all')


# * Noticeably right from the chart, I noticed that there are negative values in SalesAmount, and there are alot of 'Unknown' - missing values in CustomerGender

# In[83]:


#Check for missplelled/mistyped/extra chacracters
new_df['Channel'].value_counts()


# -> No missplelled/mistyped/extra values

# In[84]:


#Check for missplelled/mistyped/extra chacracters
new_df['OrderFrom'].value_counts()


# -> No missplelled/mistyped/extra values

# In[85]:


#Check for missplelled/mistyped/extra chacracters
new_df['Province'].value_counts()


# -> No missplelled/mistyped/extra values

# In[86]:


#Check illogical values 
new_df[new_df['SalesAmount'] <= 0]


# There are some illogical rows so I will get rid of them. 

# In[87]:


new_df.drop(new_df[new_df['SalesAmount'] <= 0].index, axis= 0, inplace= True)
new_df[new_df['SalesAmount'] <= 0].sum()


# In[88]:


#Check for null values
new_df.drop(columns= ['CustomerGender']).isna().sum()


# In[89]:


#Check for the percentage accounted by Unknown in CustomerGender
#Check for null values
new_df['CustomerGender'].value_counts(normalize= True)*100


# * I can see that 'Unknown' account for nearly 60% of the datasets, so i cannot remove these variables due to great loss of data

# In[90]:


#Check for duplicated rows
new_df.duplicated().sum()


# In[91]:


#Check for the outliers in the dataset
new_df['z_score'] = stats.zscore(df['SalesAmount'])
outliers_detect = new_df[(new_df['z_score'] >=3) | (new_df['z_score'] <=-3)]
outliers_detect.sort_values(by = 'z_score', ascending = False)


# I can see that there are 14,293 rows containing outliers in SalesAmount, but i do not know the story behind them. They can possibly be the VIP customers of the brand or in some special occasions, there are highly valued order for graduation ceremonies or local festivals. So, in reality, we have to discuss with the stakeholders about that.

# #### NOTE: After cleaning the dataset, I will discuss/report all of them with my senior DA collegue or the stakeholders to make sure we are good for the next step: Analyze phase

# # 2. Analyze and provide Insights

# In[92]:


#Calculates Sales over 3 years
pd.set_option('display.float_format', lambda x: '%.1f' % x) # This column used to display every numeric value in its true form instead of e+06 (in scientific notation)
analyze_df = new_df.copy()
analyze_df['Year'] = analyze_df['TransactionDate'].dt.year
sales_3yrs = analyze_df.groupby('Year')['SalesAmount'].sum().sort_values(ascending = False).map('{:,.1f}'.format)
sales_3yrs


# In[93]:


analyze_df['YearMonth'] = analyze_df['TransactionDate'].dt.strftime('%Y-%m')
monthly_sales = analyze_df.groupby('YearMonth')['SalesAmount'].sum().sort_index(ascending=True).reset_index()
monthly_sales.tail(10)


# The total sales of July 2023 seems quite low -> I want to check how many transactions were recorded this month. If the count is too low, I will drop rows of these records

# In[94]:


analyze_df['YearMonth'].value_counts()


# -> Better drop the count for better visualization, logic and modeling later on.

# In[95]:


analyze_df.drop(analyze_df[analyze_df['YearMonth'] == '2023-07'].index, axis= 0, inplace= True)
analyze_df[analyze_df['YearMonth'] == '2023-07'].value_counts()


# In[96]:


#Visualize Sales in each month and display year by year
analyze_df['YearMonth'] = analyze_df['TransactionDate'].dt.strftime('%Y-%m')
monthly_sales = analyze_df.groupby('YearMonth')['SalesAmount'].sum().sort_index(ascending=True).reset_index(name= 'Total Sales Amount')
avg_monthly_sales = monthly_sales['Total Sales Amount'].mean()
def billions_formatter(x, pos):
    return f'{x / 1e9:.1f}B'

fig, ax = plt.subplots(figsize = (10,6))
# Plotting the bars
monthly_sales.plot(kind='bar', ax=ax, color= 'skyblue')
# Plotting the average line
ax.axhline(avg_monthly_sales, color='red', linestyle='dashed', linewidth=2, label=f'Avg sales: {avg_monthly_sales / 1e9:.1f}B', alpha=0.7)
# Adding labels and title
ax.set_xlabel('Months in 3 years')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Total sales in each month from October 2021 to July 2023', fontsize=16)
# Set the y-axis formatter
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
# Rotating x-axis labels for better readability
ax.set_xticklabels(monthly_sales['YearMonth'], rotation=75, ha='right')
plt.show()


# * The sales by month are quite equal centering around 21 Billion VND. The month with highest value recorded was January in 2023, with about nearly 25 Billion
# * Notably, within the first 6 months of 2023, sales figures indicate that 5 out of the 6 months recorded sales below the average sales amount of 21 recored months. When compared to the corresponding period in 2022, these numbers are alarming and merit careful examination

# In[97]:


#Calculate total sales by month over 3 years
analyze_df['Month'] = analyze_df['TransactionDate'].dt.month
analyze_df['Month'] = analyze_df['Month'].map(lambda x: calendar.month_name[x])
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
total_sales_by_month = analyze_df.groupby('Month')['SalesAmount'].sum().loc[month_order].reset_index()

fig, ax = plt.subplots(figsize= (10,6))
total_sales_by_month.plot(kind= 'bar', ax= ax, color= 'skyblue')
#Adding labels and titles
ax.set_xlabel('Months')
ax.set_ylabel('Total sales amount(Billion VND)')
ax.set_title('Total sales amount in each month over 3 years', fontsize=16)
# Set the y-axis formatter
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
#Rotating x-axis for better readability
ax.set_xticklabels(total_sales_by_month['Month'], rotation = 65)
ax.legend([])
plt.show()


# * Looking at the Sales Amount in over 3 years of each month, January seemed to be the highest money-making month. It is understandable why July, August and September sales  are low.This can be explained by the provided dataset having a time span from October 2021 to July 2023 

# In[98]:


#Calculate average sales of 1 month of each year.
yearly_sales = analyze_df.groupby('Year')['SalesAmount'].sum().sort_index(ascending= True).reset_index()
month_cnt = analyze_df.groupby('Year')['YearMonth'].nunique().reset_index(name= 'MonthCount')
avg_monthly_sales = pd.merge(yearly_sales, month_cnt, on= 'Year',  how='left')
avg_monthly_sales['AverageMonthlySales'] = avg_monthly_sales['SalesAmount'] / avg_monthly_sales['MonthCount']

#Display the result
fig, ax = plt.subplots(figsize= (10,6))
avg_monthly_sales.plot(kind= 'bar',x= 'Year',y= 'AverageMonthlySales',
                        ax= ax, color= 'skyblue')
#Adding labels and titles
ax.set_xlabel('Year')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Average monthly sales in the period of 3 years', fontsize=16)
# Set the y-axis formatter
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
#Rotating x-axis for better readability
ax.set_xticklabels(avg_monthly_sales['Year'], rotation= 0)
ax.legend([])
plt.show()


# In[99]:


avg_monthly_sales


# * In this chart, 2023 was shown to have the lowest average monthly sale. I have noticed that 2021 and 2023 were not recorded with the full time span of a year so I only divide the total sales by the number of months counted. Therefore there is not enough statistic evidence to confirm whether 2023 has commercially failed.

# In[100]:


#Calculate the total sales of each quarter displayed year by year
analyze_df['Quarter'] = analyze_df['TransactionDate'].dt.to_period('Q')
quarterly_sales = analyze_df.groupby('Quarter')['SalesAmount'].sum().sort_index(ascending= True).reset_index()
quarterly_sales['Quarter'] = quarterly_sales['Quarter'].dt.strftime('%Y-Q%q')
quarterly_sales

#Display the result
fig, ax = plt.subplots(figsize= (10,6))
quarterly_sales.plot(kind= 'bar',x= 'Quarter', ax= ax, color= 'skyblue')
#Adding labels and titles
ax.set_xlabel('Quarter')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Quarterly sales in the period of 3 years', fontsize=16)
# Set the y-axis formatter
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
#Rotating x-axis for better readability
ax.set_xticklabels(quarterly_sales['Quarter'], rotation= 0)
ax.legend([])
plt.show()


# In[101]:


#Calculate the total sales in each Channel by moth
channel_sales = analyze_df.groupby(['YearMonth', 'Channel'])['SalesAmount'].sum().reset_index()
channel_sales

#Create a pivot table for the grouped data
pivot_channel_sales = channel_sales.pivot(index= 'YearMonth', columns= 'Channel', values= 'SalesAmount')

fig, ax = plt.subplots(figsize=(12,8))

#Plot a line chart
colors= {'Take Away':'skyblue', 'Delivery':'red', 'Dine In':'#FFD700'}
pivot_channel_sales.plot(kind= 'line', ax= ax, marker='o', linestyle= '-', color = colors)
#Adding labels and title
ax.set_xlabel('Months')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Total sales amount in each buying channel over 3 years', fontsize=16)
# Set the y-axis formatter
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
#Display the chart
ax.set_xticks(range(len(pivot_channel_sales.index)))
ax.set_xticklabels(pivot_channel_sales.index, rotation = 75, ha='right')
ax.legend(title='Channel')
plt.show()


# * It is clearly shown that in recent years, the trend for dining in is not popular among this pizza brand although there was a slight in revenue of this type of eating. This can be explained by the change of people dining habit since the pandemic Covid 19 which created a wave of shopping and buying online.

# In[102]:


#Calculate the total sales of each OrderFrom by month 
order_from = analyze_df.groupby(['YearMonth', 'OrderFrom'])['SalesAmount'].sum().reset_index()
order_from

#Create a pivot table for sales by OrderFrom
pivot_order_from = order_from.pivot(index= 'YearMonth', columns ='OrderFrom', values ='SalesAmount')

#Create a line chart for these data
fig, ax = plt.subplots(figsize= (12,8))
colour_style = {'CALL CENTER':'red', 'STORE':'skyblue', 'WEBSITE':'#8A2BE2', 'APP':'#00FA9A'}
pivot_order_from.plot(kind= 'line', ax= ax, marker= 'o', linestyle= '-', color= colour_style)
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
ax.set_xlabel('Months')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Sales by different order channels from October 2021 to July 2023', fontsize=16)

ax.set_xticks(range(len(pivot_order_from.index)))
ax.set_xticklabels(pivot_order_from.index, rotation = 75, ha='right')
plt.show()


# * As I can see, in recent years, people tend to order from app more frequently. The brand should be aware of this cause any trouble from using the app especially payment method may effect customer experiences. A drop in-store direct orders are inevitable cause shipping methods are more convenient and reasonably pricing nowadays.

# In[104]:


#Calculate the total sales of each OrderFrom by month 
voucher_used = analyze_df.groupby(['YearMonth', 'OrderFrom'])['VoucherStatus'].count.reset_index()
voucher_used

#Create a pivot table for sales by OrderFrom
pivot_order_from = voucher_status.pivot(index= 'YearMonth', columns ='VoucherStatus', values ='SalesAmount')

#Create a line chart for these data
fig, ax = plt.subplots(figsize= (12,8))
colour_style = {'No':'red', 'Yes':'skyblue'}
pivot_order_from.plot(kind= 'line', ax= ax, marker= 'o', linestyle= '-', color= colour_style)
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
ax.set_xlabel('Months')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Sales by voucher status from October 2021 to July 2023', fontsize=16)

ax.set_xticks(range(len(pivot_order_from.index)))
ax.set_xticklabels(pivot_order_from.index, rotation = 75, ha='right')
plt.show()


# * As I can see there is a positive signal that more revenue is generated from people using voucher, which means our promotion strategys are working or the voucher are much attractive for keeping customers retention

# In[115]:


# Create a DataFrame with counts of 'VoucherStatus' for each ('YearMonth', 'OrderFrom') group
voucher_used = analyze_df.groupby(['YearMonth', 'OrderFrom'])['VoucherStatus'].count().reset_index()

# Filter the original DataFrame for rows where 'VoucherStatus' is 'Yes'
analyze_df_voucher = analyze_df[analyze_df['VoucherStatus'] == 'Yes']

# Create a DataFrame with counts of 'VoucherStatus' for each ('YearMonth', 'OrderFrom') group for vouchers used
voucher_used_counts = analyze_df_voucher.groupby(['YearMonth', 'OrderFrom'])['VoucherStatus'].count().reset_index()

# Merge the two DataFrames on ('YearMonth', 'OrderFrom')
voucher_used = pd.merge(voucher_used, voucher_used_counts, on=['YearMonth', 'OrderFrom'], how='left')

voucher_used.rename(columns={'VoucherStatus_x': 'Total orders', 'VoucherStatus_y': 'Vouchers Used'}, inplace=True)

voucher_used['Percent of voucher usages'] = (voucher_used['Vouchers Used'] / voucher_used['Total orders'] * 100).round(2)

voucher_used


# In[118]:


#Create a pivot table for sales by OrderFrom
pivot_voucher_used = voucher_used.pivot(index= 'YearMonth', columns ='OrderFrom', values ='Percent of voucher usages')

#Create a line chart for these data
fig, ax = plt.subplots(figsize= (12,8))
colour_style = {'CALL CENTER':'red', 'STORE':'skyblue', 'WEBSITE':'#8A2BE2', 'APP':'#00FA9A'}
pivot_voucher_used.plot(kind= 'line', ax= ax, marker= 'o', linestyle= '-', color= colour_style)
ax.set_xlabel('Months')
ax.set_ylabel('Amount of vouchers used (%)')
ax.set_title('Voucher usage status in different order types from October 2021 to July 2023', fontsize=16)

ax.set_xticks(range(len(pivot_voucher_used.index)))
ax.set_xticklabels(pivot_voucher_used.index, rotation = 75, ha='right')
plt.show()


# * From the chart abvove, most of orders from store or website do not use vouchers. It can be that vouchers from these order channel are not attractive or customers do not receive many promotion actions from the brand through these 2 channels. On the other side, customers use vouchers on website and app a lot and the trends are dramatically rising. 

# In[28]:


#Calculate the total sales of each Provience by month 
sales_by_province = analyze_df.groupby(['YearMonth', 'Province'])['SalesAmount'].sum().reset_index()
sales_by_province

#Create a pivot table for sales by province 
pivot_sales_by_province = sales_by_province.pivot(index= 'YearMonth', columns ='Province', values ='SalesAmount')

#Create a line chart for these data
fig, ax = plt.subplots(figsize= (12,8))
colour_style = {'Ho Chi Minh City':'#FFD700', 'Hanoi':'skyblue', 'Nothern Provinces':'#8A2BE2', 'Southern Provinces':'#FF6F61'}
pivot_sales_by_province.plot(kind= 'line', ax= ax, marker= 'o', linestyle= '-', color= colour_style)
ax.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
ax.set_xlabel('Months')
ax.set_ylabel('Total sales amount (Billion VND)')
ax.set_title('Sales by different province by month from October 2021 to July 2023', fontsize=16)

ax.set_xticks(range(len(pivot_order_from.index)))
ax.set_xticklabels(pivot_order_from.index, rotation = 75, ha='right')
plt.show()


# * There is not many changes in the sales by province, Hanoi and Ho Chi Minh City are still top regions of sales. And these 2 places may be the locations where their targerted customers exist mostly.

# In[29]:


analyze_df


# In[30]:


#Drop the outliers for better distribution display
filtered_df = analyze_df[~((analyze_df['z_score'] >= 3) | (analyze_df['z_score'] <= -3))]
filtered_df[(filtered_df['z_score'] >= 3) | (filtered_df['z_score'] <= -3)].value_counts()


# In[31]:


filtered_df.sort_values(by= 'z_score', ascending= True)


# * Before display the average sales of 1 regular customer, I had to drop out the outliers because these sales amount are too high (there are some order even reaching 7 mil VND), and they will affect the distribution of the dataset

# In[32]:


#Display the distribution of Sales in 2022
sales_2022 = filtered_df[filtered_df['Year'] == 2022]['SalesAmount']
sales_2022

#Create a histogram on the same figure
fig, ax = plt.subplots(figsize= (14,10))

bin_width = 100000
num_bins = int((sales_2022.max() - sales_2022.min()) / bin_width)
# Define a custom formatter function for x-axis ticks
def format_thousands(x, pos):
    return f'{x / 1e3:.1f}k'
# Apply the custom formatter to the x-axis ticks
ax.xaxis.set_major_formatter(FuncFormatter(format_thousands))

#Plot the histogram
ax.hist(sales_2022, bins=num_bins, range=(sales_2022.min(), sales_2022.max()), color= 'skyblue')
ax.set_xlabel('Sales amount (Thousand VND)')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of sales in the year 2022', fontsize= 16)

plt.show()


# As I can see, the Sales variable is right skewed. Most of this brand order value from 100k VND to 400k VND, so I will expect that a normal customer will generage sales around 200-300k VND. Let's check what is the average sales per person in 2022

# In[33]:


#Calculate the average sales of 1 person in 2022 
avg_sale_by_person = filtered_df[filtered_df['Year']== 2022].groupby('CustomerID')['SalesAmount'].mean().reset_index(name= 'Avg sales of each customer')
avg_sale_1person = avg_sale_by_person['Avg sales of each customer'].mean()
print('The average sale from 1 regular customer: {:.0f} VND'.format(round(avg_sale_1person, -3)))


# From this sales figure, we can check whether it meets the company's KPIs or not, Or It will help to calculate the customer liftetime value of the company to see whether the CLV is greater than CAC (customer acquire cost) and measure the company growth. 

# In[34]:


#Display the distribution of Orders in 2022
orders_2022 = analyze_df[analyze_df['Year'] == 2022].groupby('CustomerID')['BillID'].count().reset_index(name= 'number of orders')
orders_count_2022 = orders_2022['number of orders']

#Create a histogram on the same figure
fig, ax = plt.subplots(figsize= (14,10))

bin_width = 5
num_bins = int((orders_count_2022.max() - orders_count_2022.min()) / bin_width)

#Plot the histogram
ax.hist(orders_count_2022, bins=num_bins, range=(orders_count_2022.min(), orders_count_2022.max()), color= '#FF6F61')
ax.set_xlabel('Number of orders')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of the number of orders made by all customers in the year 2022', fontsize= 16)

plt.show()


# In[35]:


# Display the distribution of Orders in 2022
orders_2022 = analyze_df[analyze_df['Year'] == 2022].groupby('CustomerID')['BillID'].count().reset_index(name='number of orders')
orders_count_2022 = orders_2022['number of orders']

# Create a boxplot on a new figure
fig, ax = plt.subplots(figsize=(14, 10))

# Plot the boxplot
ax.boxplot(orders_count_2022, vert=False)

ax.set_xlabel('Number of orders')
ax.set_title('Distribution of the number of orders made by all customers in the year 2022', fontsize=16)

plt.show()


# In[36]:


orders_2022.sort_values(by= 'number of orders', ascending= False).head(10)


# * After seeing the distribution of the order numbers in the year 2022 and display some top rows of the dataset, I was surprised that there are customers they order nearly 200 times a year, which means they eat pizza once every 2 days on average. I think there can be some mistakes of recording or they can be super VIP instead, but they are still outliers in the datasets. I will have to remove them 'temporarily' to see and understand the distribution of average orders of 1 regular customers better. 

# In[37]:


orders_2022['z_score'] = stats.zscore(orders_2022['number of orders'])
filtered_orders_2022 = orders_2022[~((orders_2022['z_score'] >=3) | (orders_2022['z_score'] <= -3))]
filtered_orders_count_2022 = filtered_orders_2022['number of orders']

fig, ax = plt.subplots(figsize= (14,10))
bins_width = 1
num_bins = int((filtered_orders_count_2022.max() - filtered_orders_count_2022.min()) / bins_width)

ax.hist(filtered_orders_count_2022, bins= num_bins, range = (filtered_orders_count_2022.min(), filtered_orders_count_2022.max()), color= '#FF6F61')
ax.set_xlabel('Number of orders')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of the number of orders made by regular customers in the year 2022', fontsize= 16)

plt.show()


# As we can see, the count for orders done one or twice in the year was highest. There was a tremendous gap between the 1st place and other places in the count of orders. This may be a sign showing that the customers' churn rate is high, their CLV of some customer group or the company's brand loyalty is low. For whatever reasons, I should dive deep into other dataset to diagnose the problem

# In[38]:


#Calculate the average orders of 1 person in 2022 
orders_2022 = analyze_df[analyze_df['Year'] == 2022].groupby('CustomerID')['BillID'].count().reset_index(name= 'number of orders')
avg_order_1person = orders_2022['number of orders'].mean()
print('The average order from 1 customer(including outliers): {:.1f} orders'.format(avg_order_1person))


# * As we can see the average order of 1 customer (including outliers) is just 1.7 orders in 1 year. This number is relatively low which indicates the low retention rate

# I want to know which months and day the stores of brand tend to be busiest so I will calculate the number of orders by months over the 3 years and number of orders in the recent year

# In[39]:


#Calculate the numbers of orders by months over 3 years
orders_count = analyze_df.groupby('YearMonth')['BillID'].count().sort_index(ascending=True).reset_index()

fig, ax = plt.subplots(figsize= (12,8))
orders_count.plot(kind= 'bar', ax= ax, color= '#FF6F61')
ax.set_xlabel('Months')
ax.set_ylabel('Number of orders')
ax.set_label('The number of orders by month over 3 years')
ax.set_xticklabels(orders_count['YearMonth'], rotation= 75)
ax.legend([])
plt.show()


# * As we can see in the period of 12 months counting from counting from June 2022, the brand saw dramatic decreases in both sales and number orders. This is a bad sign showing the business is not going well and brand should take steps to act
# 
# * Besides looking at 2022 only, we can see that early months had the highest number of orders. 

# In[40]:


#Calculate the numbers of orders by days 
filtered_df['Day'] = filtered_df['TransactionDate'].dt.strftime('%A')
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
orders_count_days = filtered_df[filtered_df['Year'] == 2022].groupby('Day')['BillID'].count().loc[day_order].reset_index()
orders_count_days

fig, ax = plt.subplots(figsize= (10,6))
orders_count_days.plot(kind= 'bar', ax= ax, color= '#FF6F61')
ax.set_xlabel('Days')
ax.set_ylabel('Total order count')
ax.set_title('Total order count in each day in the year 2022', fontsize=16)
ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xticklabels(orders_count_days['Day'], rotation = 0)
ax.legend([])
plt.show()


# * From the chart, we can see that weekends are days we receive most of the orders. If the brand tends to be busy on this day, I recommend that the brand have enough human resources on these days and provide more sales promotion to enhance the service and encourage people to buy more.

# # 3. Summary - Key analytical insights
# 1. Notably, within the first 6 months of 2023, sales figures indicate that 5 out of the 6 months recorded sales below the average sales amount of 21 recored months. When compared to the corresponding period in 2022, these numbers are alarming and merit careful examination
# 2. In recent years, the trend for dining in is not popular among this pizza brand although there was a slight in revenue of this type of eating (maybe because of the end of the pandemic). The reasons why Delivery and Dine in are significantly profit-making could be explained by the change of people dining habit since the pandemic Covid 19 which created a wave of shopping and buying online.
# 3. After launching in the beginning of 2022, sales from app rocketed significantly. In the near future, may be sales from this channel will exceed other channels of the brand
# 4. Customers use vouchers on website and app a lot and the trends are dramatically rising. In recent months, about 50-60% of orders from apps and websites are using voucher. Along with the rise of app usage, vouchers will be a key component to trigger buying needs and inrease brand revenues. 

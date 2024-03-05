#Mengimport library yang diperlukan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
sns.set(style='dark')

st.set_page_config(page_title="Bike Sharing", page_icon=":bike:", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


#Dictionary untuk memetakan kode cuaca ke nama cuaca
weather_mapping = {
    1: 'Clear',
    2: 'Mist',
    3: 'Light Rain',
    4: 'Heavy Rain'
}

#Dictionary untuk memetakan nilai workingday ke nama asli
day_mapping = {
    0: 'Holiday',
    1: 'Workday'
}


def calculate_bike_usage_by_weather(hour_data, weather_mapping):

    #Mengelompokkan data berdasarkan kondisi cuaca dan menghitung jumlah penggunaan sepeda
    weather_usage = hour_data.groupby('weathersit')['cnt'].sum().reset_index()
    
    #Menambahkan kolom baru untuk nama cuaca menggunakan mapping
    weather_usage['weather_condition'] = weather_usage['weathersit'].map(weather_mapping)
    
    #Mengembalikan DataFrame yang dihasilkan
    return weather_usage

def calculate_average_bike_usage_by_weather(hour_data, weather_mapping):

    #Mengelompokkan data berdasarkan kondisi cuaca dan menghitung rata-rata penggunaan sepeda
    weather_usage_avg = hour_data.groupby('weathersit')['cnt'].mean().reset_index()
    
    #Menambahkan kolom baru untuk nama cuaca menggunakan mapping
    weather_usage_avg['weather_condition'] = weather_usage_avg['weathersit'].map(weather_mapping)
    
    #Mengembalikan DataFrame yang dihasilkan
    return weather_usage_avg


def calculate_bike_usage_by_day_type(day_data, day_mapping):

    #Mengelompokkan data berdasarkan status hari dan menghitung jumlah penggunaan sepeda
    day_usage = day_data.groupby('workingday')['cnt'].sum().reset_index()
    
    #Menambahkan kolom baru untuk status hari menggunakan mapping
    day_usage['day_type'] = day_usage['workingday'].map(day_mapping)
    
    #Mengembalikan DataFrame yang dihasilkan
    return day_usage


def calculate_hourly_rides_return(hour_data):

    #Menghitung jumlah rides berdasarkan interval 2 jam
    hourly_rides = hour_data.groupby(hour_data['hr'] // 2)[['casual', 'registered', 'cnt']].sum()
    
    #Membuat interval label untuk sumbu x
    interval_labels = [f"{i*2}-{(i+1)*2}" for i in hourly_rides.index]
    
    #Membuat DataFrame dari hasil
    results_df = hourly_rides.reset_index()
    results_df['Interval'] = interval_labels
    results_df = results_df[['Interval', 'casual', 'registered', 'cnt']]
    
    #Mengubah nama kolom 'cnt' menjadi 'Total'
    results_df.rename(columns={'cnt': 'Total'}, inplace=True)
    
    return results_df


def calculate_hourly_rides_with_intervals(hour_data):

    #Menghitung jumlah rides berdasarkan interval 2 jam
    hourly_rides = hour_data.groupby(hour_data['hr'] // 2)[['casual', 'registered', 'cnt']].sum().reset_index()
    
    #Membuat interval label untuk sumbu x
    interval_labels = [f"{i*2}-{(i+1)*2}" for i in hourly_rides.index]
    
    return hourly_rides, interval_labels

day_df = pd.read_csv("https://raw.githubusercontent.com/emilkrrrrr/Bike-Sharing-Dataset/main/day_update.csv")
hour_df = pd.read_csv("https://raw.githubusercontent.com/emilkrrrrr/Bike-Sharing-Dataset/main/hour_update.csv")

datetime_columns = ["dteday"]
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)
 
for column in datetime_columns:
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()
 
with st.sidebar:
 
    st.image("https://raw.githubusercontent.com/emilkrrrrr/Bike-Sharing-Dataset/main/logobike (1).png")

    st.subheader('Time Range')
    start_date = st.date_input(label='Start Date', min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input(label='End Date', min_value=min_date, max_value=max_date, value=max_date)

main_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                (hour_df["dteday"] <= str(end_date))]

weather_usage = calculate_bike_usage_by_weather(main_df, weather_mapping)
weather_usage_avg = calculate_average_bike_usage_by_weather(main_df,weather_mapping)
day_usage = calculate_bike_usage_by_day_type(main_df, day_mapping)
results_df = calculate_hourly_rides_return(main_df)
results_interval_df = calculate_hourly_rides_with_intervals(main_df)
hourly_rides, interval_labels = calculate_hourly_rides_with_intervals(main_df)


st.title('Bike Sharing Dashboard🚲')

col1, col2, col3 = st.columns(3)

#Total Bike Sharing
with col1:
    with st.container():
        total_sharing = main_df['cnt'].sum()
        st.metric("Total Bike Sharing", f"{total_sharing:,}")

#Casual Orders
with col2:
    with st.container():
        total_registered = main_df['registered'].sum()
        st.metric("Registered Orders", f"{total_registered:,}")

#Registered Orders
with col3:
    with st.container():
        total_casual = main_df['casual'].sum()
        st.metric("Casual Orders", f"{total_casual:,}")


#Membuat bar chart menggunakan Plotly Express
fig = px.bar(weather_usage, y='weather_condition', x='cnt', orientation='h',
             color='cnt', color_continuous_scale=['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightgrey'],
             labels={'cnt': 'Total Bike Usage', 'weather_condition': 'Weather Condition'},
             title='Total Bike Usage by Weather Condition')
fig.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig)


#Membuat bar chart horizontal menggunakan Plotly Express
fig = px.bar(weather_usage_avg, y='weather_condition', x='cnt', orientation='h',
             color='cnt', color_continuous_scale=['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightgrey'],
             text='cnt',
             labels={'cnt': 'Average Bike Usage', 'weather_condition': 'Weather Condition'},
             title='Average Bike Usage by Weather Condition')
fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig)

st.subheader('Total and Percentage of Bike Rides by Day Type')

col1, col2 = st.columns(2)

#Diagram batang di kolom pertama
with col1:
    fig_bar = px.bar(day_usage, x='day_type', y='cnt', 
                     text='cnt',
                     color='cnt',  # Opsi ini akan memberi warna berbeda berdasarkan nilai 'cnt'
                     color_continuous_scale=['lightblue', 'lightgreen'], # Atau gunakan skala warna lain
                     labels={'cnt': 'Total Rides', 'day_type': 'Day Type'},
                     title='Total Bike Rides')
    fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_bar)

#Diagram pie di kolom kedua
with col2:
    fig_pie = px.pie(day_usage, names='day_type', values='cnt',
                     title='Percentage of Rides',
                     color='day_type',  # Memberi warna berdasarkan 'day_type'
                     color_discrete_sequence=px.colors.qualitative.Pastel)  # Menggunakan skema warna Pastel
    fig_pie.update_traces(textinfo='percent+label', pull=[0.05, 0.05], marker=dict(line=dict(color='#FFFFFF', width=2)))
    st.plotly_chart(fig_pie)

st.subheader('Bike Share Rides by Hour of Day (Interval 2 hours)')

#Hourly_rides dan interval_labels
hourly_rides, interval_labels = calculate_hourly_rides_with_intervals(main_df)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(interval_labels, hourly_rides['casual'], marker='o', linestyle='-', color='lightblue', label='Casual')
ax.plot(interval_labels, hourly_rides['registered'], marker='o', linestyle='-', color='lightgreen', label='Registered')
ax.plot(interval_labels, hourly_rides['cnt'], marker='o', linestyle='-', color='lightcoral', label='Total')
ax.set_xlabel('Hour of Day (Interval 2 hours)')
ax.set_ylabel('Number of Rides')
ax.legend()
ax.grid(True)
ax.set_xticklabels(interval_labels, rotation=45)
st.pyplot(fig)

st.caption('Copyright © 2024 Kaniakr. All rights reserved.')
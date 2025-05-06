# Names: Erin Weafer, Aidan Dilo, Thomas Evangelidis
# Project: NY Housing Market Explorer
# Description: A web app to explore housing data in New York.
# Users can search homes by city, price, and bedrooms, see top homes, averages, and view charts/maps.

# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import folium  # [EXTRA][PACKAGE]
from streamlit_folium import folium_static


# [DA1] Data Cleaning & Loading
df = pd.read_csv("NY-House-Dataset.csv")
df.dropna(inplace=True)

# Sidebar for navigation
st.sidebar.title("NY Housing Explorer")
page = st.sidebar.radio("Choose a section:", 
                        ("Top 10 Expensive Homes", 
                         "Filter Homes", 
                         "Averages by City", 
                         "Visualizations"))

# [PY1] Function with two parameters
#ChatGPT-assisted: Prompt used — “Write a Python function that returns the top 10 most expensive homes
# in a given city from a housing dataset with columns like 'PRICE' and 'LOCALITY'.”
#Uses: pandas — for filtering and sorting tabular data efficiently
def top_expensive_homes(data, city_name):
    homes_in_city = data[data['LOCALITY'] == city_name]
    return homes_in_city.sort_values(by='PRICE', ascending=False).head(10)

# [PY2] Function returning multiple values
# Uses: pandas — .mean() makes it easy to calculate column-wise averages
def calculate_averages(data, city_name):
    homes = data[data['LOCALITY'] == city_name]
    return homes['PRICE'].mean(), homes['PROPERTYSQFT'].mean()

# [PY3] Using Lists
cities = sorted(df['LOCALITY'].dropna().unique())

# [PY4] Dictionary Example
city_dict = {city: i for i, city in enumerate(cities)}

# Page 1: Top 10 Expensive Homes
if page == "Top 10 Expensive Homes":
    st.header("Top 10 Most Expensive Homes by City")
    selected_city = st.selectbox("Pick a City:", cities)  # [ST1]
    top_homes = top_expensive_homes(df, selected_city)
    st.dataframe(top_homes)

# Page 2: Filter Homes
elif page == "Filter Homes":
    st.header("Find Homes Under Your Budget")
    selected_city = st.selectbox("Pick a City:", cities, key='filter')
    max_price = st.slider("Max Price ($):", 50000, 10000000, 500000)  # [ST2]
    min_beds = st.number_input("Min Number of Bedrooms:", min_value=1, max_value=10, value=3) # [ST3]

    # ChatGPT-assisted: Prompt used — "How can I filter a pandas DataFrame for homes in a specific city
    # that cost less than a user-defined price and have at least a certain number of bedrooms?"
    # Show homes in that city under the price and with enough bedrooms
    filtered_homes = df[(df['LOCALITY'] == selected_city) & 
                        (df['PRICE'] <= max_price) & 
                        (df['BEDS'] >= min_beds)]
    st.dataframe(filtered_homes)

# Page 3: Averages by City
elif page == "Averages by City":
    st.header("Average Price and Size in a City")
    selected_city = st.selectbox("Pick a City:", cities, key='avg')
    avg_price, avg_sqft = calculate_averages(df, selected_city)
    st.write(f"Average Price: ${avg_price:,.2f}")
    st.write(f"Average Size: {avg_sqft:,.2f} sqft")

# Page 4: Visualizations
# Bar chart and histogram use matplotlib for static visualizations.
# Seaborn is used for enhanced statistical plots like boxplots and scatterplots.
# Libraries:
# matplotlib.pyplot: Core plotting library for Python, great for line, bar, and histogram charts
# seaborn: Built on top of matplotlib, allows for more elegant and informative statistical visuals
elif page == "Visualizations":
    st.header("See the Data in Charts and Maps")

    # Filter extreme outliers for cleaner charts
    filtered_df = df[df['PRICE'] < 10000000]
    filtered_df2 = df[(df['PRICE'] < 10000000) & (df['BEDS'] < 10)]

    # [CHART1] Bar Chart - Average Home Price by City
    # ChatGPT-assisted: Prompt used — “How do I plot a horizontal bar chart in Streamlit using matplotlib
    # for average home prices by city from a pandas DataFrame?”

    st.subheader("Average Home Price by City")
    avg_price_by_city = filtered_df.groupby('LOCALITY')['PRICE'].mean().sort_values()
    fig1, ax1 = plt.subplots()
    avg_price_by_city.plot(kind='barh', ax=ax1, color='skyblue')
    ax1.set_xlabel("Average Price ($)")
    ax1.set_ylabel("City")
    ax1.set_title("Average Home Price by City")
    st.pyplot(fig1)

    # [CHART2] Histogram - Price Distribution
    st.subheader("How Home Prices Are Spread Out")
    fig2, ax2 = plt.subplots()
    ax2.hist(filtered_df['PRICE'], bins=30, color='lightgreen', edgecolor='black')
    ax2.set_xlabel("Price ($)")
    ax2.set_ylabel("Number of Homes")
    ax2.set_title("Price Distribution (Homes under $10M)")
    st.pyplot(fig2)

    # [MAP] Map of Home Locations
    # ChatGPT-assisted: Prompt used — “How can I show home locations on an interactive map in Streamlit using PyDeck
    # with a scatterplot layer based on latitude and longitude?”
    st.subheader("Map of Home Locations")
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=df['LATITUDE'].mean(),
            longitude=df['LONGITUDE'].mean(),
            zoom=7,
            pitch=50,
        ),
        # Uses: pydeck
        # Enables interactive scatterplot layers over a real map
        # Good for plotting many geographic points (like home locations)
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[LONGITUDE, LATITUDE]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
            ),
        ],
    ))

    # [SEA1] Seaborn Chart - Beds vs Price
    # ChatGPT-assisted: Prompt used — “How can I make a boxplot of price versus number of bedrooms using
    # seaborn in Streamlit, but only include homes under $10M and with fewer than 10 bedrooms?”
    st.subheader("Price Compared to Bedrooms")
    fig3, ax3 = plt.subplots()
    sns.boxplot(x='BEDS', y='PRICE', data=filtered_df2, ax=ax3)
    ax3.set_title("Price vs Bedrooms (Beds < 10, Price < $10M)")
    st.pyplot(fig3)

    # [EXTRA][SEA2] Seaborn Scatterplot [EXTRA][SEA2]
    st.subheader("Scatterplot of Square Footage vs Price")
    fig4, ax4 = plt.subplots()
    sns.scatterplot(x='PROPERTYSQFT', y='PRICE', data=filtered_df, ax=ax4)
    ax4.set_title("Square Footage vs Price (Filtered)")
    st.pyplot(fig4)

# [EXTRA][FOLIUM1], [EXTRA][FOLIUM2]: Folium map
# ChatGPT-assisted: Prompt used — “How do I create a folium map in Streamlit that shows a circle marker
# for each home with popups showing the city name?”
# Uses: folium + streamlit_folium to embed interactive maps with Python
elif page == "Folium Map":
    st.header("Folium Map of Home Locations")
    m = folium.Map(location=[df['LATITUDE'].mean(), df['LONGITUDE'].mean()], zoom_start=7)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=3,
            popup=row['LOCALITY'],
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)
    folium_static(m)

# [ST4] Customized page design: Sidebar Navigation
st.sidebar.caption("Made by Erin, Aidan, and Thomas")

# [EXTRA][DA2] Sorting example:
df = df.sort_values(by='PRICE', ascending=False)

# [DA3] Find Top 10 expensive already done
# [DA4] Filter by city done
# [DA5] Filter by multiple conditions done
# [EXTRA][DA7] Create new grouped column
price_categories = pd.cut(df['PRICE'], bins=[0, 500000, 1000000, 5000000, 10000000], labels=["<$500K", "$500K-$1M", "$1M-$5M", "$5M-$10M"])
df['PriceRange'] = price_categories

# [EXTRA][DA9] Add a new column (Price per SqFt)
# ChatGPT-assisted: Prompt used — “How do I create a new column in pandas that calculates price per square foot
# from 'PRICE' and 'PROPERTYSQFT'?”
df['Price_per_SqFt'] = df['PRICE'] / df['PROPERTYSQFT']

# Reference:
# [EXTRA][PACKAGE]: Used folium and streamlit_folium for interactive mapping.
# See section 1 of AI usage report if applicable.




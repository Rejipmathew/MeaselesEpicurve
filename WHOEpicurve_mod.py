import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# Load the Measles data from the CSV file
@st.cache_data  # Cache the data for faster loading
def load_data():
    df = pd.read_csv(r"https://raw.githubusercontent.com/Rejipmathew/MeaselesEpicurve/main/407-table-web-measles-cases-by-month%20-%20WEB.csv")
    return df

df = load_data()

# Get unique countries and years
countries = df['Country'].unique()
years = df['Year'].unique()

# Streamlit app title
st.title("Measles Epicurve App")

# Sidebar for selecting country
selected_country = st.sidebar.selectbox("Select Country", countries)

# Create pages using st.radio
page = st.sidebar.radio("Select Page", ["Trend Plot", "Epicurve Plot", "Map"])

if page == "Trend Plot":
    # --- Trend Plot ---
    st.subheader("Trend of Measles Cases Over the Years")

    # Preprocessing: Convert relevant columns to numeric, coercing errors to NaN
    for col in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate yearly totals for the selected country
    yearly_totals = df[df['Country'] == selected_country].groupby('Year').sum(numeric_only=True)

    # Create the trend plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(yearly_totals.index, yearly_totals.sum(axis=1), marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Number of Cases")
    ax.set_title(f"Trend of Measles Cases in {selected_country}")
    plt.grid(True)
    st.pyplot(fig)

elif page == "Epicurve Plot":
    # --- Epicurve Plot ---
    st.subheader("Epicurve for Selected Year")
    selected_year = st.sidebar.selectbox("Select Year", years)

    # Filter data based on selected country and year
    filtered_df = df[(df['Country'] == selected_country) & (df['Year'] == selected_year)]

    # Prepare data for the epicurve
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    # Extract case numbers, handling potential NaN values
    cases = filtered_df[months].values.tolist()
    if cases:
        cases = cases[0]
    else:
        cases = [0] * 12

    # Calculate total cases for the year, handling NaN values
    total_cases = np.nansum(cases)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar plot with case numbers on top (handling NaN values)
    bars = ax.bar(months, cases, color='skyblue')
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Cases")
    ax.set_title(f"Measles Cases in {selected_country} ({selected_year})")

    plt.xticks(rotation=45)

    for bar in bars:
        height = bar.get_height()
        if not np.isnan(height):
            ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Display total number of cases
    st.write(f"**Total Cases for {selected_year}: {total_cases}**")

    st.pyplot(fig)

elif page == "Map":
    # --- Map ---
    st.subheader("Map of Selected Country")

    # Select the year for the map
    selected_year = st.sidebar.selectbox("Select Year for Map", years)

    # Filter data for the selected year
    filtered_df = df[(df['Year'] == selected_year)] 

    # Calculate total cases for each country
    filtered_df['Total Cases'] = filtered_df[["January", "February", "March", "April", "May", "June", 
                                             "July", "August", "September", "October", "November", "December"]].sum(axis=1)

    # Create the map using plotly.express with a larger size
    fig = px.choropleth(
        filtered_df, 
        locations="Country", 
        locationmode='country names', 
        hover_name="Country",
        color="Total Cases",
        color_continuous_scale='YlOrRd',
        projection='natural earth',
        title=f"Measles Cases by Country in {selected_year}",
        width=1600,  # Set the width of the map
        height=1000   # Set the height of the map
    )

    # Display the map
    st.plotly_chart(fig)

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

# Create pages using st.sidebar.radio
page = st.sidebar.radio("Select Page", ["Home", "Trend Plot", "Epicurve Plot", "Map"])

if page == "Home":
    # --- Home Page ---
    st.subheader("Welcome to the Measles Epicurve Dashboard!")
    st.write("""
    This interactive dashboard allows you to explore measles case data across different countries and years. 
It provides three main visualizations to help you understand the trends and patterns of measles outbreaks:

**1. Trend Plot:**

* **See the big picture:** This plot displays the overall trend of measles cases over time for a selected country. 
* **Identify outbreaks:**  Notice any spikes or declines in cases over the years, indicating potential outbreaks or the impact of vaccination campaigns.
* **How to use:**
    * Select a country from the "Select Country" dropdown in the sidebar.
    * The plot will automatically update to show the trend of measles cases for that country over all available years.

**2. Epicurve Plot:**

* **Monthly breakdown:**  This plot provides a detailed view of measles cases for a specific year in a selected country, broken down by month.
* **Seasonal patterns:** Observe any seasonal trends in measles cases.
* **How to use:**
    * Select a country from the "Select Country" dropdown in the sidebar.
    * Choose a year from the "Select Year" dropdown in the sidebar.
    * The plot will update to show the monthly distribution of measles cases for that year and country.

**3. Map:**

* **Global view:** This map provides a geographical representation of measles cases across different countries for a selected year.
* **Identify hotspots:** Easily spot countries with high numbers of cases, indicated by darker colors on the map.
* **How to use:**
    * Select a year from the "Select Year for Map" dropdown in the sidebar.
    * The map will display total measles cases for each country in that year.
    * Hover over a country to see its name and the total number of cases.
    * The selected country from the sidebar will be highlighted with a red marker.

**Navigating the Dashboard:**

* **Page selection:** Use the radio buttons in the sidebar to switch between the "Trend Plot", "Epicurve Plot", and "Map" pages.
* **Country selection:** The "Select Country" dropdown in the sidebar allows you to choose the country for which you want to see data in the Trend Plot and Epicurve Plot.
* **Year selection:**  You can select specific years for the Epicurve Plot and the Map using the respective dropdowns in the sidebar.

**Tips for Using the Dashboard:**

* **Explore different countries and years:**  Change the selections in the sidebar to analyze measles trends in various regions and time periods.
* **Look for patterns:** Pay attention to any recurring trends, spikes, or declines in the plots and map.
* **Combine visualizations:** Use the information from all three visualizations together to gain a comprehensive understanding of the measles data.

    **Navigate to other pages using the sidebar.**
    """)

elif page == "Trend Plot":
    # --- Trend Plot ---
    st.subheader("Trend of Measles Cases Over the Years")

    # Sidebar for selecting country (only on this page)
    selected_country = st.sidebar.selectbox("Select Country", countries)

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

    # Sidebar for selecting country and year (only on this page)
    selected_country = st.sidebar.selectbox("Select Country", countries)
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

    # Sidebar for selecting country and year for the map (only on this page)
    selected_country = st.sidebar.selectbox("Select Country", countries)  
    selected_year = st.sidebar.selectbox("Select Year for Map", years)

    # Filter data for the selected year
    filtered_df = df[(df['Year'] == selected_year)] 

    # Calculate total cases for each country
    filtered_df['Total Cases'] = filtered_df[["January", "February", "March", "April", "May", "June", 
                                             "July", "August", "September", "October", "November", "December"]].sum(axis=1)

    # Convert 'Total Cases' to integers for the year 2011
    if selected_year == 2011:
        filtered_df['Total Cases'] = filtered_df['Total Cases'].astype(int)

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
        width=1200,  # Set the width of the map
        height=800   # Set the height of the map
    )

    # Highlight the selected country on the map
    fig.update_geos(
        fitbounds="locations", 
        visible=False, 
        showcountries=True,
        countrycolor="black",
        scope="world"
    )
    fig.add_scattergeo(
        locations=[selected_country],
        locationmode='country names',
        marker=dict(size=10, color="red")
    )

    # Display the map
    st.plotly_chart(fig)

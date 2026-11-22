import streamlit as st
import pandas as pd
from streamlit_extras.let_it_rain import *

page_chosen = st.sidebar.radio("🌤️ Pages",["Home Page", "Log Observation", "Dashboard", "Search", "View All Data"])
st.subheader(":orange[Weather Tracker]")

uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.weather_data = pd.read_csv(uploaded_file)
        st.session_state.uploaded_file_name = uploaded_file.name

elif "weather_data" not in st.session_state:
    st.session_state.weather_data = pd.read_csv("weather_tracker.csv")

weather_tracker = st.session_state.weather_data

# PAGE 1: HOME
if page_chosen == "Home Page":
    st.title("👋 Hello! Welcome back!")
    st.subheader(":orange[🌤️ Your Weather Tracker]")
    st.write("Let's see what the weather has been up to!")
    st.divider()

    yesterday = weather_tracker.iloc[-1]
    condition = yesterday["Condition"]

    st.subheader(f"Yesterday's weather was :blue[{condition}]")
    st.write(f"📅 Date: {yesterday['Date']}")

    left, mid, right = st.columns(3)
    left.metric("🌡️ Temperature", f"{yesterday['Temperature']} °C")
    mid.metric("💧 Humidity", f"{yesterday['Humidity']}%")
    right.metric("💨 Wind Speed", f"{yesterday['Wind Speed']} km/h")

    activities = {"Sunny": "☀️ Go for a walk or have a picnic outside!",
        "Cloudy": "☁️ Enjoy a relaxing walk in the park.",
        "Rainy": "🌧️ Cozy up at home under a blanket.",
        "Windy": "💨 Stay in and enjoy a board game.",
        "Stormy": "⛈️ Stay indoors and watch a movie.",
        "Foggy": "🌫️ Have a warm drink and read a book.",
        "Snowy": "❄️ Build a snowman or relax with a warm drink."}

    st.subheader(":green[🎯 Suggested Activity]")
    st.success(activities[condition])
    st.divider()
    st.write(f"📋 Total Observations: **{len(weather_tracker)}**")
    st.write(f"📆 Days Recorded: **{weather_tracker['Date'].nunique()}**")

# PAGE 2: LOG OBSERVATION
if page_chosen == "Log Observation":
    st.title("📝 Log Weather Observation")
    st.write("Add a new weather observation to your tracker!")

    with st.form("weather_form"):
        day = st.date_input("📅 Date")
        temperature = st.number_input("🌡️ Temperature (°C)",step=1)
        condition = st.selectbox("🌤️ Condition", ["Sunny", "Cloudy", "Rainy", "Windy", "Stormy", "Foggy", "Snowy"])
        humidity = st.number_input("💧 Humidity (%)", step=1)
        wind_speed = st.number_input("💨 Wind Speed (km/h)", step=1)
        save = st.form_submit_button("💾 Save Observation")
        

    if save:
        new_row = pd.DataFrame([{"Date": str(day),
            "Temperature": temperature,
            "Condition": condition,
            "Humidity": humidity,
            "Wind Speed": wind_speed}])

        weather_tracker = pd.concat([weather_tracker, new_row], ignore_index=True)
        st.session_state.weather_data = weather_tracker
        weather_tracker.to_csv("weather_tracker.csv", index=False)
        st.success("✅ Observation saved! Great job keeping track of the weather.")

        if condition == "Snowy":
            st.snow()
        elif condition == "Rainy":
            rain(emoji="☔",font_size=54,falling_speed=14,animation_length="short",)
        elif condition == "Sunny":
            rain(emoji="☀️",font_size=54,falling_speed=14,animation_length="short",)
        elif condition == "Cloudy":
            rain(emoji="☁️",font_size=54,falling_speed=14,animation_length="short",)
        elif condition == "Stormy":
            rain(emoji="⛈️",font_size=54,falling_speed=14,animation_length="short",)
        elif condition == "Windy":
            rain(emoji="🍃",font_size=54,falling_speed=14,animation_length="short",)
        elif condition == "Foggy":
            rain(emoji="🌫️",font_size=54,falling_speed=14,animation_length="short",)        

    st.subheader(":blue[📋 Recent Observations]")
    st.dataframe(weather_tracker.tail(5), use_container_width=True)

# PAGE 3: DASHBOARD
if page_chosen == "Dashboard":
    st.title("📊 Weather Dashboard")
    st.write("Your temperature statistics at a glance!")

    left, middle, right = st.columns(3)
    with left:
        with st.container(border=True):
            st.markdown("#### :blue[🌡️ Average]")
            st.metric("Average Temperature", f"{weather_tracker['Temperature'].mean():.2f} °C")
    with middle:
        with st.container(border=True):
            st.markdown("#### :green[❄️ Minimum]")
            st.metric("Minimum Temperature", f"{weather_tracker['Temperature'].min():} °C")
    with right:
        with st.container(border=True):
            st.markdown("#### :orange[🔥 Maximum]")
            st.metric("Maximum Temperature", f"{weather_tracker['Temperature'].max():} °C")

    st.subheader(":blue[📈 Temperature Over Time]")
    st.line_chart(weather_tracker.round({"Temperature": 1}).sort_values("Date"), x="Date", y="Temperature")

    hottest = weather_tracker.loc[weather_tracker["Temperature"].idxmax()]
    coldest = weather_tracker.loc[weather_tracker["Temperature"].idxmin()]

    st.subheader("🏆 Temperature Records")
    st.warning(f"🔥 Hottest: {hottest['Temperature']:} °C on {hottest['Date']}")
    st.info(f"❄️ Coldest: {coldest['Temperature']:} °C on {coldest['Date']}")

# PAGE 4: SEARCH
if page_chosen == "Search":
    st.title("🔎 Search Weather")
    st.write("Find observations by :blue[date], :green[weather condition] or both! ✌🏻")

    search_by = st.radio("Search by", ["Date", "Condition", "Both"], horizontal=True)
    results = weather_tracker

    if search_by in ["Date", "Both"]:
        day = st.date_input("📅 Select a date")
        results = results[results["Date"] == str(day)]

    if search_by in ["Condition", "Both"]:
        condition = st.selectbox("🌤️ Select a condition", sorted(weather_tracker["Condition"].unique()))
        results = results[results["Condition"] == condition]

    st.subheader(":blue[📋 Search Results]")
    st.write(f"🔍 Found **{len(results)}** observation(s)")
    st.dataframe(results, use_container_width=True)

# PAGE 5: VIEW ALL DATA
if page_chosen == "View All Data":
    st.title("📋 All Weather Data")
    st.write("🌦️ Every observation, all in one place!")
    st.write(f"📌 **{len(weather_tracker)}** observations recorded")
    st.dataframe(weather_tracker, use_container_width=True)
    st.download_button("⬇️ Download CSV", weather_tracker.to_csv(index=False), "weather_history.csv")

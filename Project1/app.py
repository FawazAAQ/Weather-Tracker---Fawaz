from pathlib import Path
import pandas as pd
import streamlit as st

from myutils import (WEATHER_COLUMNS,add_observation,filter_observations,read_weather_csv,temperature_summary,)

try:
    from streamlit_extras.let_it_rain import rain
except ModuleNotFoundError:
    rain = None

page_chosen = st.sidebar.radio("🌤️ Pages",["Home Page", "Log Observation", "Dashboard", "Search", "View All Data"])
st.subheader(":orange[Weather Tracker]")

uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if "weather_data" not in st.session_state:     # Initialize the session once. The starter CSV is next to this py file.
    starter_csv = Path(__file__).with_name("weather_tracker.csv")
    if starter_csv.exists():
        st.session_state.weather_data = read_weather_csv(starter_csv)
    else:
        st.session_state.weather_data = pd.DataFrame(columns=WEATHER_COLUMNS)

if uploaded_file is None:
    st.session_state.pop("weather_upload", None)
else:
    upload_key = (uploaded_file.name, uploaded_file.getvalue())   # Compare file contents so a new CSV with the same name still loads.
    if st.session_state.get("weather_upload") != upload_key:
        try:
            uploaded_file.seek(0)
            observations = read_weather_csv(uploaded_file)
        except ValueError as error:
            st.sidebar.error(f"Could not load the CSV: {error}")
        else:
            st.session_state.weather_data = observations
            st.session_state.weather_upload = upload_key

weather_tracker = st.session_state.weather_data

# PAGE 1: HOME
if page_chosen == "Home Page":
    st.title("👋 Hello! Welcome back!")
    st.subheader(":orange[🌤️ Your Weather Tracker]")
    st.write("Let's see what the weather has been up to!")
    st.divider()

    if weather_tracker.empty:
        st.info("Upload a CSV or log an observation to get started.")

    yesterday = weather_tracker.iloc[-1]  # Gets last record of the csv
    condition = yesterday["Condition"]

    st.subheader(f"Yesterday's weather was :blue[{condition}]")
    st.write(f"📅 Date: {yesterday['Date']}")

    left, mid, right = st.columns(3)
    left.metric("🌡️ Temperature", f"{yesterday['Temperature']} °C")
    mid.metric("💧 Humidity", f"{yesterday['Humidity']}%")                      # Puts the metrics in order left center right 
    right.metric("💨 Wind Speed", f"{yesterday['Wind Speed']} km/h")

    activities = {"Sunny": "☀️ Go for a walk or have a picnic outside!",       # Initiliaze activities for each condition
        "Cloudy": "☁️ Enjoy a relaxing walk in the park.",
        "Rainy": "🌧️ Cozy up at home under a blanket.",
        "Windy": "💨 Stay in and enjoy a board game.",
        "Stormy": "⛈️ Stay indoors and watch a movie.",
        "Foggy": "🌫️ Have a warm drink and read a book.",
        "Snowy": "❄️ Build a snowman or relax with a warm drink."}

    st.subheader(":green[🎯 Suggested Activity]")
    st.success(activities.get(condition, "Check the latest conditions before heading out."))
    st.divider()
    st.write(f"📋 Total Observations: **{len(weather_tracker)}**")                              # A record of the total rows
    st.write(f"📆 Days Recorded: **{weather_tracker['Date'].nunique()}**")                      # A record of the total unique dates 

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
        # Keep edits in this session so users can export them as a CSV.
        weather_tracker = add_observation(weather_tracker, day, temperature, condition, humidity, wind_speed)
        st.session_state.weather_data = weather_tracker
        st.success("✅ Observation saved! Great job keeping track of the weather.")

        if condition == "Snowy":
            st.snow()
        elif rain is None:
            st.balloons()
        else:
            weather_emoji = {"Rainy": "☔", "Sunny": "☀️", "Cloudy": "☁️", "Stormy": "⛈️", "Windy": "🍃", "Foggy": "🌫️",} 
            rain(emoji=weather_emoji[condition], font_size=54, falling_speed=14, animation_length="short")
            # Drops the corrosponding emoji as confetti when a record is made

    st.subheader(":blue[📋 Recent Observations]")
    st.dataframe(weather_tracker.tail(5), use_container_width=True)

# PAGE 3: DASHBOARD
if page_chosen == "Dashboard":
    st.title("📊 Weather Dashboard")
    st.write("Your temperature statistics at a glance!")

    summary = temperature_summary(weather_tracker)
    if summary is None:
        st.info("Log an observation with a temperature to see the dashboard.")
        st.stop()

    average, coldest, hottest = summary
    left, middle, right = st.columns(3)
    with left:
        with st.container(border=True):
            st.markdown("#### :blue[🌡️ Average]")
            st.metric("Average Temperature", f"{average:.2f} °C")
    with middle:
        with st.container(border=True):
            st.markdown("#### :green[❄️ Minimum]")
            st.metric("Minimum Temperature", f"{coldest['Temperature']} °C")
    with right:
        with st.container(border=True):
            st.markdown("#### :orange[🔥 Maximum]")
            st.metric("Maximum Temperature", f"{hottest['Temperature']} °C")

    st.subheader(":blue[📈 Temperature Over Time]")
    st.line_chart(weather_tracker.round({"Temperature": 1}).sort_values("Date"), x="Date", y="Temperature")

    st.subheader("🏆 Temperature Records")
    st.warning(f"🔥 Hottest: {hottest['Temperature']:} °C on {hottest['Date']}")
    st.info(f"❄️ Coldest: {coldest['Temperature']:} °C on {coldest['Date']}")

# PAGE 4: SEARCH
if page_chosen == "Search":
    st.title("🔎 Search Weather")
    st.write("Find observations by :blue[date], :green[weather condition] or both! ✌🏻")

    search_by = st.radio("Search by", ["Date", "Condition", "Both"], horizontal=True)
    day = None
    condition = None

    if search_by in ["Date", "Both"]:
        day = st.date_input("📅 Select a date")

    if search_by in ["Condition", "Both"]:
        conditions = sorted(weather_tracker["Condition"].dropna().unique())
        if not conditions:
            st.info("Log an observation to search by condition.")
            st.stop()

        condition = st.selectbox("🌤️ Select a condition", conditions)

    results = filter_observations(weather_tracker, day, condition)
    st.subheader(":blue[📋 Search Results]")
    st.write(f"🔍 Found **{len(results)}** observations")
    st.dataframe(results, use_container_width=True)

# PAGE 5: VIEW ALL DATA
if page_chosen == "View All Data":
    st.title("📋 All Weather Data")
    st.write("🌦️ Every observation, all in one place!")
    st.write(f"📌 **{len(weather_tracker)}** observations recorded")
    st.dataframe(weather_tracker, use_container_width=True)
    st.download_button("⬇️ Download CSV",weather_tracker.to_csv(index=False),"weather_history.csv",mime="text/csv")

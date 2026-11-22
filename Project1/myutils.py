import pandas as pd

WEATHER_COLUMNS = ["Date", "Temperature", "Condition", "Humidity", "Wind Speed"]

def read_weather_csv(source):  # Load a CSV and check that it has the columns the app uses.
    observations = pd.read_csv(source, dtype={"Date": str, "Condition": str})
    missing_columns = [column for column in WEATHER_COLUMNS if column not in observations]
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

    for column in ("Temperature", "Humidity", "Wind Speed"):
        observations[column] = pd.to_numeric(observations[column])

    return observations

def add_observation(observations, day, temperature, condition, humidity, wind_speed): # Return the weather history with the new observation added.
    new_row = pd.DataFrame([{"Date": str(day), "Temperature": temperature, "Condition": condition, "Humidity": humidity, "Wind Speed": wind_speed, }])

    if observations.empty:
        return new_row.reindex(columns=observations.columns)

    return pd.concat([observations, new_row], ignore_index=True)


def temperature_summary(observations):   # Return the average temperature and the coldest and hottest observations.
    temperatures = observations["Temperature"].dropna()
    if temperatures.empty:
        return None

    return (
        temperatures.mean(),
        observations.loc[temperatures.idxmin()],
        observations.loc[temperatures.idxmax()],
    )


def filter_observations(observations, day=None, condition=None):  # Filter by date, condition, or both when the caller supplies them
    if day is not None:
        observations = observations[observations["Date"] == str(day)]

    if condition is not None:
        observations = observations[observations["Condition"] == condition]

    return observations

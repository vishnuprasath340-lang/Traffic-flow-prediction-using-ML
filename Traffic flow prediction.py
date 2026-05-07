import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# -----------------------------
# Load Dataset
# -----------------------------

data = pd.read_csv(r"C:\Users\Ashley nikhil\OneDrive\Desktop\traffic flow\traffic.csv")

# -----------------------------
# Handle Missing Values
# -----------------------------

data = data.fillna(data.mean(numeric_only=True))

# -----------------------------
# Feature Selection
# -----------------------------

X = data[['hour','day','month','temp','rain','snow','clouds']]
y = data['traffic_volume']

# -----------------------------
# Train Model
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

# -----------------------------
# Streamlit UI
# -----------------------------

st.title("🚦 Traffic Flow Prediction System")

st.write("Machine Learning based Traffic Volume Prediction")

st.sidebar.header("Enter Traffic Conditions")

hour = st.sidebar.slider("Hour",0,23,12)
day = st.sidebar.slider("Day",1,31,15)
month = st.sidebar.slider("Month",1,12,6)

temp = st.sidebar.number_input("Temperature (K)",270,320,295)

rain = st.sidebar.slider("Rain (mm)",0,10,0)
snow = st.sidebar.slider("Snow (mm)",0,5,0)

clouds = st.sidebar.slider("Cloud Coverage (%)",0,100,50)

input_data = np.array([[hour,day,month,temp,rain,snow,clouds]])

# -----------------------------
# Prediction
# -----------------------------

if st.button("Predict Traffic"):

    prediction = model.predict(input_data)

    st.success(f"Predicted Traffic Volume: {int(prediction[0])}")

    if prediction < 2000:
        st.info("Traffic Level: Low")

    elif prediction < 4000:
        st.warning("Traffic Level: Medium")

    else:
        st.error("Traffic Level: Heavy")

# -----------------------------
# Show Dataset
# -----------------------------

st.subheader("Dataset Preview")

st.dataframe(data.head())
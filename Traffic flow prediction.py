import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

# --- DB ENGINE ---
class FarmDB:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'your_password', # UPDATE THIS
            'database': 'SmartFarmDB'
        }

    def execute(self, query, params=None, fetch=False):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        res = cursor.fetchall() if fetch else None
        conn.commit()
        cursor.close()
        conn.close()
        return res

db = FarmDB()

# --- SENSOR SIMULATOR (To impress the examiner) ---
def simulate_iot_data(field_id):
    # Simulating data that would come from an ESP32/Arduino
    temp = round(random.uniform(20.0, 35.0), 2)
    hum = round(random.uniform(40.0, 70.0), 2)
    moisture = round(random.uniform(10.0, 50.0), 2)
    db.execute("INSERT INTO sensor_logs (field_id, temperature, humidity, soil_moisture) VALUES (%s, %s, %s, %s)",
               (field_id, temp, hum, moisture))

# --- UI COMPONENTS ---
def dashboard_view():
    st.title("🚜 SmartFarm AI Dashboard")
    
    # 1. Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    active_fields = db.execute("SELECT COUNT(*) as count FROM fields", fetch=True)[0]['count']
    crops_growing = db.execute("SELECT COUNT(*) as count FROM plantings WHERE status='Growing'", fetch=True)[0]['count']
    
    col1.metric("Total Land", f"{active_fields} sectors")
    col2.metric("Active Crops", crops_growing)
    
    # 2. Real-time Monitoring
    st.subheader("📡 Live Field Telemetry")
    selected_field = st.selectbox("Select Field Sector", db.execute("SELECT * FROM fields", fetch=True), 
                                 format_func=lambda x: x['field_name'])
    
    if st.button("Refresh IoT Feed"):
        simulate_iot_data(selected_field['field_id'])
        st.toast("New sensor data synchronized!")

    # Fetch latest logs
    logs = db.execute("SELECT * FROM sensor_logs WHERE field_id = %s ORDER BY recorded_at DESC LIMIT 20", 
                     (selected_field['field_id'],), fetch=True)
    
    if logs:
        df = pd.DataFrame(logs)
        
        # Gauge Chart for Current Moisture
        current_moisture = float(df.iloc[0]['soil_moisture'])
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_moisture,
            title = {'text': "Current Soil Moisture %"},
            gauge = {
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 15], 'color': "red"},
                    {'range': [15, 30], 'color': "green"},
                    {'range': [30, 100], 'color': "blue"}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 20}
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Trend Chart
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df['recorded_at'], y=df['temperature'], name="Temp (°C)"))
        fig_trend.add_trace(go.Scatter(x=df['recorded_at'], y=df['humidity'], name="Humidity (%)"))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No sensor data available for this sector yet.")

def crop_management():
    st.title("🌱 Planting & Crop Lifecycle")
    
    with st.form("new_planting"):
        st.write("### Register New Planting")
        f_id = st.selectbox("Field", db.execute("SELECT * FROM fields", fetch=True), format_func=lambda x: x['field_name'])
        c_id = st.selectbox("Crop", db.execute("SELECT * FROM crops", fetch=True), format_func=lambda x: x['crop_name'])
        p_date = st.date_input("Planting Date")
        if st.form_submit_button("Start Planting Session"):
            db.execute("INSERT INTO plantings (field_id, crop_id, planting_date) VALUES (%s, %s, %s)",
                       (f_id['field_id'], c_id['crop_id'], p_date))
            st.success("Planting Logged!")

    st.divider()
    st.write("### Current Field Status")
    status_data = db.execute("""
        SELECT p.planting_id, f.field_name, c.crop_name, p.planting_date, p.status 
        FROM plantings p
        JOIN fields f ON p.field_id = f.field_id
        JOIN crops c ON p.crop_id = c.crop_id
    """, fetch=True)
    if status_data:
        st.table(pd.DataFrame(status_data))

def analytics_view():
    st.title("📈 Agricultural Analytics")
    # Show average moisture per field
    analysis = db.execute("""
        SELECT f.field_name, AVG(s.soil_moisture) as avg_moisture
        FROM fields f
        LEFT JOIN sensor_logs s ON f.field_id = s.field_id
        GROUP BY f.field_name
    """, fetch=True)
    df_analysis = pd.DataFrame(analysis)
    st.bar_chart(df_analysis.set_index('field_name'))

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="SmartFarm OS", layout="wide")
    
    st.sidebar.title("🍀 SmartFarm OS")
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2765/2765012.png", width=100)
    
    page = st.sidebar.selectbox("Navigate", ["Real-time Dashboard", "Crop Management", "Resource Analytics"])
    
    if page == "Real-time Dashboard":
        dashboard_view()
    elif page == "Crop Management":
        crop_management()
    elif page == "Resource Analytics":
        analytics_view()

if __name__ == "__main__":
    main()
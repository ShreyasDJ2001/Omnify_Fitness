import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title="Fitness Booking", page_icon="🏋️", layout="wide")

BASE_URL = "http://127.0.0.1:5000"

# Sidebar Navigation
st.sidebar.title("📋 Navigation")
menu = st.sidebar.radio("", ["Home", "Available Classes", "Book a Class", "View Bookings", "All Bookings"])


# Home Page
if menu == "Home":
    st.markdown("<h1 style='text-align: center;'> Fitness Booking System</h1>", unsafe_allow_html=True)


    # Center-align the welcome message
    st.markdown("<h4 style='text-align: center;'>Welcome to the Fitness Booking App!</h4>", unsafe_allow_html=True)


# Available Classes
elif menu == "Available Classes":
    st.title("📅 Available Classes")
    st.markdown("#### Select Timezone to View Class Schedules")

    timezone = st.selectbox("🌍 Select Timezone", ["Asia/Kolkata", "America/New_York", "Europe/London"])
    
    if st.button("🔍 Get Classes"):  # Only fetch data when button is clicked
        response = requests.get(f"{BASE_URL}/classes-by-timezone?timezone={timezone}")
        
        if response.status_code == 200:
            data = response.json()

            if data:
                # Reorder the keys in each class object to desired column order
                reordered_data = [
                    {
                        "class_id": cls["id"],
                        "name": cls["name"],
                        "instructor": cls["instructor"],
                        "date_time": cls["date_time"],
                        "available_slots": cls["available_slots"]
                    }
                    for cls in data
                ]

                st.markdown("***Class Schedule:***")
                st.dataframe(reordered_data, use_container_width=True)
            else:
                st.info("No classes available for the selected timezone.")



# Book a Class
elif menu == "Book a Class":
    st.title("📝 Book a Class")

    st.markdown("#### Enter Booking Details Below")
    col1, col2 = st.columns([1, 2])

    with col1:
        class_id = st.number_input("🎯 Enter Class ID", min_value=1, step=1)
        timezone = st.selectbox("🌍 Select Timezone", ["Asia/Kolkata", "America/New_York", "Europe/London"])

    with col2:
        client_name = st.text_input("👤 Your Name")
        client_email = st.text_input("📧 Your Email")
        local_time = st.text_input("⏳ Enter Local Time (YYYY-MM-DD HH:MM)")

    if st.button("Book Now"):
        payload = {
            "class_id": class_id,
            "client_name": client_name,
            "client_email": client_email,
            "timezone": timezone,
            "local_time": local_time
        }
        response = requests.post(f"{BASE_URL}/book", json=payload)
        if response.status_code == 201:
            st.success("🎉 Booking successful!")
        else:
            st.error(f"⚠ {response.json().get('error', 'Booking failed')}")

# View My Bookings
elif menu == "View Bookings":
    st.title("📜 My Bookings")

    email = st.text_input("📧 Enter Email to View Bookings")

    if st.button("🔍 Get Bookings"):
        response = requests.get(f"{BASE_URL}/bookings?email={email}")
        if response.status_code == 200:
            data = response.json()
            with st.expander("🔽 View Booking Details"):
                st.dataframe(data, use_container_width=True)  # Use expander for better UX
        else:
            st.error("⚠ No bookings found")

# View All Bookings
elif menu == "All Bookings":
    st.title("📃 All Bookings")

    response = requests.get(f"{BASE_URL}/all-bookings")
    if response.status_code == 200:
        data = response.json()
        with st.expander("🔽 View All Booking Details"):
            st.dataframe(data, use_container_width=True)  # More structured display
    else:
        st.error("⚠ Could not fetch booking data")

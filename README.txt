# Fitness Class Booking API

## Introduction
This project provides a RESTful API to manage fitness class schedules and bookings. Users can view available classes based on their timezone, book classes, and see their booking history. A Streamlit-based UI is also included for a more user-friendly experience.

## Getting Started

Follow the steps below to set up the project on your local system.

### 1. Create and Activate Virtual Environment
python -m venv venv

venv\Scripts\activate

### 2. Install Required Packages
 
pip install -r requirements.txt
 

### 3. Seed the Database with Sample Data
This populates the database with sample fitness classes.
 
python seed_data.py
 

### 4. Run the API Server
To start the API server, run:
 
python run.py
 

## API Endpoints

You can test the following endpoints using Postman or cURL.

### 1. Get All Classes
 
GET http://localhost:5000/classes
 

### 2. Get Bookings by User Email
 
GET http://localhost:5000/bookings?email=john@example.com
 

### 3. Get All Bookings (Admin View)
 
GET http://localhost:5000/all-bookings
 

### 4. Get Classes by Timezone
 
GET http://localhost:5000/classes-by-timezone?timezone=America/New_York
 

### 5. Book a Class
 
POST http://localhost:5000/book
 
**Sample Request Body (raw JSON):**
 
{
    "class_id": 2,
    "client_name": "nikhil",
    "client_email": "nikhil@example.com",
    "timezone": "Asia/Kolkata",
    "local_time": "2025-06-20 07"
}


## Running the UI

To run the Streamlit UI, execute the following commands in separate terminals:


Start-Process -FilePath "python" -ArgumentList "run.py"
Start-Process -FilePath "streamlit" -ArgumentList "run app_ui.py"


Once started, the Streamlit app will launch in your default web browser.

## Contribute

Feel free to open issues or submit pull requests if you'd like to improve or expand the functionality of this project.

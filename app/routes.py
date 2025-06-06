from flask import Blueprint, request, jsonify
from .models import FitnessClass, Booking
from .database import db
from datetime import datetime
import pytz
import logging
import re

logging.basicConfig(filename='app.log', level=logging.INFO)

main = Blueprint('main', __name__)

def is_valid_email(email):
    """ Validates email format. """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def convert_time(dt, target_tz):
    """ Converts UTC time to user's timezone """
    target_zone = pytz.timezone(target_tz)
    return dt.astimezone(target_zone)

def convert_to_utc(local_time, local_tz="Asia/Kolkata"):
    """ Converts local time to UTC for storing in DB """
    tz = pytz.timezone(local_tz)
    localized_time = tz.localize(local_time)
    return localized_time.astimezone(pytz.utc)

@main.route('/', methods=['GET'])
def home():
    """ Home endpoint to check API status. """
    try:
        logging.info("Home endpoint accessed.")
        return jsonify({"message": "Fitness Booking API is running!"}), 200
    except Exception as e:
        logging.exception("Error accessing home endpoint.")
        return jsonify({'error': 'Internal Server Error'}), 500
        
@main.route('/classes', methods=['GET'])
def get_classes():
    """ Fetch all fitness classes adjusted for user's timezone & display in readable format. """
    try:
        user_timezone = request.args.get("timezone", "Asia/Kolkata")  

        classes = FitnessClass.query.all()
        if not classes:
            logging.warning("No fitness classes found.")
            return jsonify({'error': 'No classes available'}), 404

        data = [{
            'id': cls.id,
            'name': cls.name,
            'date_time': convert_time(cls.date_time, user_timezone).strftime('%d-%m-%Y %I:%M %p'),  # Readable format
            'instructor': cls.instructor,
            'available_slots': cls.available_slots
        } for cls in classes]

        logging.info(f"Retrieved {len(classes)} fitness classes for timezone {user_timezone}.")
        return jsonify(data), 200

    except Exception as e:
        logging.exception("Unexpected error in fetching classes.")
        return jsonify({'error': 'Internal Server Error'}), 500



@main.route('/book', methods=['POST'])
def book_class():
    """ Book a fitness class with proper validation. """
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        name = data.get('client_name')
        email = data.get('client_email')
        user_tz = data.get('timezone', "Asia/Kolkata")  # Default IST
        local_time_str = data.get('local_time')  # User's requested date/time (YYYY-MM-DD HH:MM format)

        if not all([class_id, name, email, local_time_str]):
            logging.warning("Booking failed: Missing fields.")
            return jsonify({'error': 'Missing fields'}), 400

        if not is_valid_email(email):
            logging.warning("Booking failed: Invalid email format.")
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate `client_name` 
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z ]{2,}", name.strip()):
            logging.warning(f"Booking failed: Invalid client name - {name}")
            return jsonify({'error': 'Invalid name. Name must contain only letters and spaces (min 2 characters).'}), 400


        # Validate the date format BEFORE processing
        try:
            user_local_dt = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            logging.warning(f"Booking failed: Invalid date format provided - {local_time_str}")
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM'}), 400

        fitness_class = FitnessClass.query.get(class_id)

        if not fitness_class:
            logging.error(f"Booking failed: Class ID {class_id} not found.")
            return jsonify({'error': 'Class not found'}), 404

        if fitness_class.available_slots <= 0:
            logging.error(f"Booking failed: No slots left for Class ID {class_id}.")
            return jsonify({'error': 'No slots available'}), 400

        # Convert user's requested local time to UTC
        utc_time = convert_to_utc(user_local_dt, user_tz)

        # Validate if requested date matches available class date
        if utc_time.date() != fitness_class.date_time.date():
            logging.warning(f"Booking failed: Requested date {utc_time.date()} does not match available slot ({fitness_class.date_time.date()}).")
            return jsonify({'error': 'Time slots are not available for this date.'}), 400

        booking = Booking(
            class_id=class_id,
            client_name=name,
            client_email=email,
        )

        fitness_class.available_slots -= 1
        db.session.add(booking)
        db.session.commit()

        logging.info(f"Booking successful for {name} in Class ID {class_id}. Requested Date: {utc_time.date()}, Class Date: {fitness_class.date_time.date()}")
        return jsonify({
            'message': 'Booking successful',
            'class_time_utc': utc_time.isoformat(),
            'timezone': user_tz
        }), 201

    except Exception as e:
        logging.exception("Unexpected error in booking process.")
        return jsonify({'error': 'Internal Server Error'}), 500




def format_datetime(dt_str):
    """ Convert API timestamp into a readable format (DD-MM-YYYY HH:MM AM/PM) """
    try:
        dt_obj = datetime.fromisoformat(dt_str)
        return dt_obj.strftime('%d-%m-%Y %I:%M %p')  # Example: "06-10-2025 06:00 PM"
    except ValueError:
        return dt_str  # If formatting fails, return the original string

@main.route('/bookings', methods=['GET'])
def get_bookings():
    """ Fetch bookings for a specific client with timezone handling. """
    try:
        email = request.args.get('email')
        user_timezone = request.args.get("timezone", "Asia/Kolkata")  # Default IST

        if not email:
            logging.warning("Booking retrieval failed: Missing email parameter.")
            return jsonify({'error': 'Email is required'}), 400

        bookings = Booking.query.filter_by(client_email=email).all()

        if not bookings:
            logging.warning(f"No bookings found for email: {email}.")
            return jsonify({'error': 'No bookings found'}), 404

        data = [{
            'id': b.id,
            'class_name': b.fitness_class.name,
            'date_time': format_datetime(convert_time(b.fitness_class.date_time, user_timezone).isoformat()),  # Apply formatting
            'instructor': b.fitness_class.instructor
        } for b in bookings]

        logging.info(f"Retrieved {len(bookings)} bookings for email: {email}. Timezone: {user_timezone}.")
        return jsonify(data), 200

    except Exception as e:
        logging.exception("Unexpected error in fetching bookings.")
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/all-bookings', methods=['GET'])
def get_all_bookings():
    """ Fetch all bookings in the system with timezone conversion. """
    try:
        user_timezone = request.args.get("timezone", "Asia/Kolkata")  # Default IST

        bookings = Booking.query.all()

        if not bookings:
            logging.warning("No bookings found in the system.")
            return jsonify({'error': 'No bookings available'}), 404

        data = [{
            'id': b.id,
            'class_name': b.fitness_class.name,
            'date_time': format_datetime(convert_time(b.fitness_class.date_time, user_timezone).isoformat()),
            'instructor': b.fitness_class.instructor,
            'client_name': b.client_name,
            'client_email': b.client_email
        } for b in bookings]

        logging.info(f"Retrieved {len(bookings)} total bookings. Timezone: {user_timezone}.")
        return jsonify(data), 200

    except Exception as e:
        logging.exception("Unexpected error in fetching all bookings.")
        return jsonify({'error': 'Internal Server Error'}), 500


@main.route('/classes-by-timezone', methods=['GET'])
def get_classes_by_timezone():
    """ Fetch all classes, converting timings to the user's timezone. """
    try:
        user_timezone = request.args.get("timezone", "Asia/Kolkata")  # Default to IST if not provided

        # Validate timezone input
        if user_timezone not in pytz.all_timezones:
            logging.warning(f"Invalid timezone provided: {user_timezone}")
            return jsonify({'error': 'Invalid timezone'}), 400

        classes = FitnessClass.query.all()
        if not classes:
            logging.warning("No fitness classes found.")
            return jsonify({'error': 'No classes available'}), 404

        data = [{
            'id': cls.id,
            'name': cls.name,
            'date_time': convert_time(cls.date_time, user_timezone).strftime('%d-%m-%Y %I:%M %p'),  # Convert to requested timezone
            'instructor': cls.instructor,
            'available_slots': cls.available_slots
        } for cls in classes]

        logging.info(f"Retrieved {len(classes)} classes in timezone: {user_timezone}")
        return jsonify(data), 200

    except Exception as e:
        logging.exception("Unexpected error in fetching classes by timezone.")
        return jsonify({'error': 'Internal Server Error'}), 500

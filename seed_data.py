from app import create_app
from app.database import db
from app.models import FitnessClass
from datetime import datetime, timedelta
import pytz

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    classes = [
        FitnessClass(name="Yoga", date_time=ist.localize(datetime(2025, 10, 6, 9, 0)), instructor="Anjali", available_slots=20),   # 9:00 AM
        FitnessClass(name="Yoga", date_time=ist.localize(datetime(2025, 10, 7, 10, 0)), instructor="Rahul", available_slots=10),   # 10:00 AM
        FitnessClass(name="Zumba", date_time=ist.localize(datetime(2025, 10, 8, 8, 30)), instructor="Priya", available_slots=5),   # 8:30 AM
        FitnessClass(name="HIIT", date_time=ist.localize(datetime(2025, 6, 20, 7, 0)), instructor="Shreyas", available_slots=2),   # 7:00 AM
        FitnessClass(name="HRX", date_time=ist.localize(datetime(2025, 6, 10, 6, 0)), instructor="Shreyas", available_slots=5)     
    ]


    db.session.bulk_save_objects(classes)
    db.session.commit()

    print("Seed data inserted successfully!")

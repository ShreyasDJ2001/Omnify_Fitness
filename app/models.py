from .database import db
from datetime import datetime

class FitnessClass(db.Model):
    __tablename__ = 'fitness_classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    def set_time_in_utc(self, local_time, local_tz="Asia/Kolkata"):
        tz = pytz.timezone(local_tz)
        localized_time = tz.localize(local_time)
        self.date_time = localized_time.astimezone(pytz.utc)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_classes.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    fitness_class = db.relationship('FitnessClass', backref=db.backref('bookings', lazy=True))

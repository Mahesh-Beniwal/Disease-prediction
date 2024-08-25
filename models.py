from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates,relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'

    patient_id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)  # Updated column name
    age = Column(Integer, default=None)  # New column for age
    mobile_no = Column(String(20), default=None)  # New column for mobile number
    gender = Column(String(10), default=None)  # New column for gender
    address = Column(Text)  # New column for address

    # diagnoses = relationship("Diagnoses", back_populates="patient")

    @property
    def password(self):
        """Read-only property for password"""
        return self.password_hash

    @password.setter
    def password(self, value):
        """Hashes the password before storing"""
        self.password_hash = generate_password_hash(value)  # Hash password

    @validates('password')
    def validate_password(self, key, password):
        """Ensures password complexity"""
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain an uppercase letter")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain a number")
        if not any(char in "!@#$%^&*()" for char in password):
            raise ValueError("Password must contain a special character")
        return password

    def __repr__(self):
        return f"<Patient {self.patient_id}, {self.full_name}>"

    def verify_password(self, password):
        """Verifies a password against the stored hash"""
        return check_password_hash(self.password_hash, password)

# class Diagnoses(Base):
#     __tablename__ = 'diagnoses'

#     diagnosis_id = Column(Integer, primary_key=True)
#     patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
#     visit_date = Column(DateTime, nullable=False)
#     diagnosis_text = Column(Text)

#     # Define relationship with Patient
#     patient = relationship("Patient", back_populates="diagnoses")

#     def __repr__(self):
#         return f"<Diagnoses {self.diagnosis_id}, Patient ID: {self.patient_id}, Visit Date: {self.visit_date}>"


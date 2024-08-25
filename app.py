import csv
from datetime import date
import os
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from database import SessionLocal
from models import  Patient
from flask_cors import CORS
# ------------------------------------------------------------------------------- Model Imports
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC


app = Flask(__name__)
CORS(app, resources={r"/process_data": {"origins": "*", "methods": ["POST", "OPTIONS"]}})
app.config['SECRET_KEY'] = 'h@rdT0cr@ck'

predicted_disease = None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        patient = db.query(Patient).filter_by(email=email).first()

        if patient and check_password_hash(patient.password_hash, password):
            session['user_id'] = patient.patient_id
            db.close()
            return jsonify({"status": "success", "redirect": "/dashboard"}) # Redirect to dashboard after login
        else:
            db.close()
            return jsonify({"status": "error", "message": "Invalid credentials"})

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        new_patient = Patient(full_name=full_name, email=email, password_hash=hashed_password)

        db = SessionLocal()
        try:
            db.add(new_patient)
            db.commit()
            db.close
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            return f"Error: {str(e)}"
        finally:
            db.close()

    return render_template("signup.html")
# ------------------------------------------------------------------------------
# @app.route("/dashboard")
# def dashboard():
#     if not session.get('user_id'):
#         return redirect(url_for('index'))
    
#     # Retrieve patient details from the database
#     db = SessionLocal()
#     try:
#         user_id = session['user_id']
#         patient = db.query(Patient).filter_by(patient_id=user_id).first()
#         db.close()
#         return render_template("dashboard.html", patient=patient)
#     except Exception as e:
#         db.close()
#         return f"Error: {str(e)}"

@app.route("/dashboard")
def dashboard():
    print("function called")
    if not session.get('user_id'):
        return redirect(url_for('index'))
    
    # Retrieve patient details from the database
    db = SessionLocal()
    try:
        user_id = session['user_id']
        patient = db.query(Patient).filter_by(patient_id=user_id).first()
        db.close()
        return render_template("dashboard.html", patient=patient)
    except Exception as e:
        db.close()
        return f"Error: {str(e)}"
    
@app.route('/patient_details')
def patient_details():
    # Get user ID from session
    user_id = session.get('user_id')

    # If user is not logged in, return an error message
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Retrieve patient details from the database
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter_by(patient_id=user_id).first()
        db.close()

        # Return patient details as JSON
        return jsonify({
            'full_name': patient.full_name,
            'age': patient.age,
            'mobile_no': patient.mobile_no,
            'gender': patient.gender
        })
    except Exception as e:
        db.close()
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------------
@app.route("/diagnosis")
def diagnosis():
    return render_template("diagnosis.html")


# Above this the code will word good.
# Code of the model -------------------------------------------------------------------------------------------------------------------

def predict_disease(symptoms):
    # Load the data into a pandas dataframe
    training = pd.read_csv('Data/DatasetALL.csv')

    # Select the columns to use as input features
    All_features = training.columns[:-1]

    # Select the target attribute as the last column of the original dataframe
    Target = training['prognosis']

    # Handle missing values using the SimpleImputer class
    imputer = SimpleImputer(strategy='mean')
    x = imputer.fit_transform(training[All_features])

    # Encode categorical variables using the LabelEncoder class
    le = LabelEncoder()
    Target = le.fit_transform(Target)

    # Scale numerical features using the StandardScaler class
    scaler = StandardScaler()
    x = scaler.fit_transform(x)

    # Create a dictionary to map symptom names to numerical features
    symptom_dict = {col: i for i, col in enumerate(All_features)}

    # Define a function to encode the input symptoms as numerical features
    def encode_symptoms(symptoms):
        features = [0] * len(All_features)
        for symptom in symptoms:
            if symptom in symptom_dict:
                features[symptom_dict[symptom]] = 1
        return features

    # Encode the input symptoms as numerical features
    encoded_symptoms = encode_symptoms(symptoms)

    encoded_symptoms = np.array(encoded_symptoms)

    encoded_symptoms = encoded_symptoms.reshape(1, -1)
    # Create an SVM model
    model = SVC()

    # Fit the model to the training data
    model.fit(x, Target)

    # Make a prediction for the input symptoms
    prediction = model.predict(encoded_symptoms)
    prediction = le.inverse_transform(prediction)
    print(prediction[0])
    return prediction[0]

# 
# -----------------------------------------------------------------------------------------------------------------

@app.route('/process_data', methods=['POST', 'OPTIONS'])
def process_data():
    global predicted_disease
    if request.method == 'POST':
        print("Function called")
        selected_options = request.json
        print("Selected Options:", selected_options)

        unique_selected_options = list(set(selected_options))
        
        # Call the predict_disease function with unique selected options and store the result in the global variable
        predicted_disease = predict_disease(unique_selected_options)
        print("Predicted Disease Stored:", predicted_disease)
        # --------------------------------------------------
        # db = SessionLocal()
        # new_diagnosis = Diagnoses(patient_id=session.get('user_id'), visit_date=date.today(), diagnosis_text=predicted_disease)
        # db.add(new_diagnosis)
        # db.commit()
        # db.close()

        
        # --------------------------------------------------
        # Do whatever you want with the selected options here
        return 'Data received successfully', 200
    elif request.method == 'OPTIONS':
        # Respond to OPTIONS request
        response = jsonify({'message': 'Allowed'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response



@app.route('/result')
def show_result():
    return render_template('results.html')

# ----------------------------------------------------------------------

@app.route('/save_details', methods=['POST'])
def save_details():
    # Get form data
    print("function called")
    age = request.form.get('age')
    mobile_no = request.form.get('mobile_no')
    gender = request.form.get('gender')
    address = request.form.get('address')

    # Get user ID from session
    user_id = session.get('user_id')

    # If user is not logged in, redirect to login page
    if not user_id:
        return redirect(url_for('index'))

    # Save details to the database
    db = SessionLocal()
    try:
        # Retrieve user object from database
        patient = db.query(Patient).filter_by(patient_id=user_id).first()

        # Update patient details
        patient.age = age
        patient.mobile_no = mobile_no
        patient.gender = gender
        patient.address = address

        db.commit()
        return "Data saved successfully."
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"
    finally:
        db.close()
# -----------------------------------------------------------------------------

@app.route('/api/results', methods=['GET'])
def get_patient_details():
    print("Function Called")
    # Check if a session is already present
    user_id = session.get('user_id')

    # If user is not logged in, return an error message
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Retrieve patient details from the database
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter_by(patient_id=user_id).first()
        db.close()

        # Fetch the disease name from the global variable
        disease_name = predicted_disease

        # Fetch the disease description from the CSV file
        disease_description = None
        data_folder = os.path.join(os.path.dirname(__file__), 'Data')
        with open(os.path.join(data_folder, 'symptom_Description.csv'), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == disease_name:
                    disease_description = row[1]
                    break

        # Fetch the precautions from the CSV file
        precautions = []
        with open(os.path.join(data_folder, 'symptom_precaution.csv'), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == disease_name:
                    for precaution in row[1:]:
                        precautions.append(precaution)
                    break

        # Return the patient details, disease name, disease description, and precautions as a JSON response
        return jsonify({
            'patient_name': patient.full_name,
            'age': patient.age,
            'gender': patient.gender,
            'mobile_no': patient.mobile_no,
            'email_id': patient.email,
            'disease_name': disease_name,
            'disease_description': disease_description,
            'precaution_1': precautions[0] if len(precautions) > 0 else None,
            'precaution_2': precautions[1] if len(precautions) > 1 else None,
            'precaution_3': precautions[2] if len(precautions) > 2 else None,
            'precaution_4': precautions[3] if len(precautions) > 3 else None
        })
    except Exception as e:
        db.close()
        return f"Error: {str(e)}"


@app.route("/logout")
def logout():
  session.pop('user_id', None)  # Remove user ID from session
  return redirect(url_for('index'))  # Redirect to login page

if __name__ == "__main__":
    app.run(debug=True)



# The code below have to debug..
# @app.route("/save_details", methods=["POST"])
# def save_details():
#     print("Inside save_details function")  # Add this print statement to check if the function is called
#     if request.method == "POST":
#         print("Request method is POST")  # Add this print statement to check if the request method is POST
#         # Retrieve form data
#         mobile_no = request.form.get("mobile_no")
#         age = request.form.get("age")
#         gender = request.form.get("gender")
#         address = request.form.get("address")
#         print("Form data retrieved:", mobile_no, age, gender, address)  # Print the retrieved form data

#         # Get user ID from session
#         user_id = session.get('user_id')
#         print("User ID from session:", user_id)  # Print the user ID retrieved from the session

#         # If user is not logged in, redirect to login page
#         if not user_id:
#             print("User is not logged in")  # Add this print statement to check if the user is logged in
#             return redirect(url_for('index'))

#         # Save details to the database
#         db = SessionLocal()
#         try:
#             # Retrieve user object from database
#             patient = db.query(Patient).filter_by(patient_id=user_id).first()
#             print("Patient details before update:", patient)  # Print the patient details before update

#             # Update patient details
#             patient.mobile_no = mobile_no
#             patient.age = age
#             patient.gender = gender
#             patient.address = address
#             print("Patient details after update:", patient)  # Print the patient details after update

#             db.commit()
#             print("Details saved successfully.")
#             return "Details saved successfully."
#         except Exception as e:
#             db.rollback()
#             print("Error:", e)  # Print the error message if an exception occurs
#             return f"Error: {str(e)}"
#         finally:
#             db.close()

#     return redirect(url_for('dashboard'))  # Redirect to dashboard after saving details

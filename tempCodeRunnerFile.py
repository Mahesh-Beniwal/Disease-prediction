mport csv
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
import streamlit as st
import pandas as pd
import datetime
import random
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------------------------
# SESSION STORAGE
# ---------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "otp" not in st.session_state:
    st.session_state.otp = None

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def calculate_age(dob):
    today = datetime.date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def send_otp():
    otp = str(random.randint(1000, 9999))
    st.session_state.otp = otp
    return otp

def generate_pdf(user, result):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Healthcare Assistant Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Patient Details</b>", styles["Heading2"]))
    story.append(Paragraph(f"Name: {user['first_name']} {user['last_name']}", styles["Normal"]))
    story.append(Paragraph(f"DOB: {user['dob']}", styles["Normal"]))
    story.append(Paragraph(f"Age: {user['age']}", styles["Normal"]))
    story.append(Paragraph(f"Gender: {user['gender']}", styles["Normal"]))
    story.append(Paragraph(f"Mobile: {user['mobile']}", styles["Normal"]))
    story.append(Paragraph(f"Email: {user['email']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Prediction Result</b>", styles["Heading2"]))
    for k, v in result.items():
        story.append(Paragraph(f"{k.capitalize()}: {v}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Disclaimer:</b> This is not a medical diagnosis.", styles["Normal"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def predict(symptoms):
    if "fever" in symptoms and "cough" in symptoms:
        return {
            "Condition": "Viral Respiratory Infection",
            "Severity": "Moderate",
            "Doctor": "General Physician",
            "Medicine": "Paracetamol, Cough Syrup",
            "Advice": "Rest and drink fluids"
        }
    return {
        "Condition": "Common Cold",
        "Severity": "Mild",
        "Doctor": "General Physician",
        "Medicine": "Paracetamol",
        "Advice": "Rest"
    }

# ---------------------------
# LOGIN / REGISTER PAGE
# ---------------------------
st.title("🩺 AI Healthcare Assistant")

if not st.session_state.logged_in:
    option = st.radio("Choose Option", ["Login", "Register"])

    if option == "Register":
        st.subheader("Register")

        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        dob = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email ID")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Send OTP"):
            otp = send_otp()
            st.info(f"OTP Sent (Demo OTP: {otp})")

        otp_input = st.text_input("Enter OTP")

        if st.button("Register"):
            if otp_input != st.session_state.otp:
                st.error("Invalid OTP")
            else:
                age = calculate_age(dob)
                st.session_state.users[username] = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "dob": str(dob),
                    "age": age,
                    "gender": gender,
                    "mobile": mobile,
                    "email": email,
                    "password": password
                }
                st.success("Registration successful!")

    if option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = st.session_state.users.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Login Successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ---------------------------
# MAIN APP
# ---------------------------
user = st.session_state.users[st.session_state.current_user]

st.sidebar.success(f"Logged in as {user['first_name']}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

st.header("Symptom Checker")

symptoms = st.multiselect(
    "Select Symptoms",
    ["fever", "cough", "fatigue", "headache", "chest pain", "shortness of breath"]
)

if st.button("Predict"):
    result = predict(symptoms)

    st.subheader("Prediction Result")
    for k, v in result.items():
        st.write(f"**{k}:** {v}")

    pdf = generate_pdf(user, result)
    st.download_button(
        "📄 Download PDF Report",
        pdf,
        file_name="health_report.pdf",
        mime="application/pdf"
    )

st.caption("⚠️ Educational purpose only. Consult a doctor for real medical advice.")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import pandas as pd

# Firebase setup (replace with your actual Firebase credentials path)
cred = credentials.Certificate("C:/Users/Asus/Downloads/expense-tracker-8f276-firebase-adminsdk-yhcrb-094292163c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Streamlit app layout
st.title("Smart Expense Tracker")
st.sidebar.header("Add a New Expense")

# Input fields for new expenses
amount = st.sidebar.number_input("Amount", min_value=0)
category = st.sidebar.selectbox("Category", ["Food", "Rent", "Utilities", "Entertainment", "Other"])
date = st.sidebar.date_input("Date")

if st.sidebar.button("Add Expense"):
    # Save the new expense to Firebase
    db.collection("expenses").add({
        "amount": amount,
        "category": category,
        "date": date.strftime("%Y-%m-%d")
    })
    st.sidebar.success("Expense added!")

# Fetch expenses from Firebase
expenses_ref = db.collection("expenses").stream()
data = [{"amount": doc.to_dict().get("amount"),
         "category": doc.to_dict().get("category"),
         "date": doc.to_dict().get("date")} for doc in expenses_ref]

# Convert data to DataFrame
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Display table
st.header("Expense Summary")
st.write(df)

# Visualization section
if not df.empty:
    # Monthly Expenses Line Chart
    st.subheader("Monthly Expense Trend")
    monthly_expense = df.groupby(df['date'].dt.to_period("M")).sum().reset_index()
    monthly_expense['date'] = monthly_expense['date'].dt.to_timestamp()  # Convert to timestamp for plotting
    fig = px.line(monthly_expense, x='date', y='amount', title='Monthly Expenses')
    st.plotly_chart(fig)

    # Category Distribution Pie Chart
    st.subheader("Expenses by Category")
    category_expense = df.groupby("category").sum().reset_index()
    fig = px.pie(category_expense, values='amount', names='category', title='Expenses by Category')
    st.plotly_chart(fig)

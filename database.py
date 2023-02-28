import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta
from dotenv import load_dotenv # pip install python-dotenv
import os

# Load the environment variables
# load_dotenv(".env")
# DETA_KEY = os.getenv("DETA_KEY")

DETA_KEY = "d03ajqv1_pfPUggjR1k6aTKZwQZ3xx2PYF5qsG139"
# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("monthly_reports")


def insert_period(period, incomes, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)


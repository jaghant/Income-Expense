import os
import calendar  # Core Python Module
from datetime import datetime  # Core Python Module
import streamlit as st # pip install streamlit
from streamlit_option_menu import option_menu # pip install streamlit-option-menu
import plotly.graph_objects as go # pip install plotly
import database as db # local import
from PIL import Image




#--------SETTINGS-------------
incomes = ["Salary"]
expenses = ["Rent", "Utilities", "Groceries", "Buspar", "Other Expenses", "Saving"]
currency = "Rs"
page_title = "Income and Expense Tracker"
page_icon = ":money_with_wings:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)


# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])


#------DATABASE INTEFASE-----------
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods
# -----HIDE STREAMLIT STYLE ----
# hide_st_style = """
#                 <style>
#                 #MainMenu {Visibility: hidden;}
#                 footer {visibility: hidden;}
#                 header {visibility: hidden;}
#                 </style>
#                 """ 
# st.markdown(hide_st_style, unsafe_allow_html=True)                
#------NAVIGATION MENU---------
with st.sidebar:
     image = Image.open('logo.png')
     st.image(image,  width = 200)
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Visualization"],
        icons=["pencil-square", "bar-chart-fill"], 
        orientation="parallel",
)

# --- INPUT & SAVE PERIODS ---
if selected == "Data Entry":
    st.header(f"Data Entry in {currency}")
    with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")
            
            
            "---"
            with st.expander("Income"):
                for income in incomes:
                    st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
            with st.expander("Comment"):
                comment = st.text_area("", placeholder="Enter a comment here ....")
                
            "---"
            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
                incomes = {income: st.session_state[income] for income in incomes}
                expenses = {expense: st.session_state[expense] for expense in expenses}
                db.insert_period(period, incomes, expenses, comment)
                st.success("Data saved!")  
                st.balloons()
            
#------PLOT RERIODS------
if selected == "Visualization":
    st.header("Visualization")  
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot Period") 
        if submitted:
            # get data form database
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            expenses = period_data.get("expenses")
            incomes = period_data.get("incomes")
        
                    
            # create metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")
            
            # Create sankey chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

                # Plot it!
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)          

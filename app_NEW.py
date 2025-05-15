from flask import Flask, render_template, request
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Main calculation function
def calculate_chart_data(
    loan_type: int, annual_salary, inflation_rate,
    salary_growth_rate, debt_amount, lump_sum_amount, savings_growth_rate, graduation_year
):
    # Set the current year
    current_year = datetime.now().year
    outstanding_years = ((graduation_year + 1) + (30 if loan_type == 2 else 40)) - current_year
    total_months = 12 * outstanding_years

    # Initialize variables for calculation loop
    savings_amount = 0
    student_loan_savings_from_lump_sum = 0
    end_saving_amount = 0
    student_loan_savings_from_lump_sum_end_amount = 0
    debt_less_lump_sum = max(debt_amount - lump_sum_amount, 0)
    end_debt_less_lump_sum = debt_less_lump_sum
    chart_list = []
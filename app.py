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
    loan_type: int, annual_salary, inflation_rate, loan_interest_rate,
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

    # Main calculation loop
    for month in range(1, total_months + 1):
        year = (month - 1) // 12 + 1
        year_salary = round(annual_salary * ((1 + salary_growth_rate) ** (year - 1)), 2)

        # Monthly repayment calculation based on loan type
        if loan_type == 2:
            monthly_repayment_amount = round(((year_salary - 27295) * 0.09) / 12, 2)
        elif loan_type == 5:
            monthly_repayment_amount = round(((year_salary - 25000) * 0.09) / 12, 2)
        else:
            monthly_repayment_amount = 0

        # Interest added to the full loan amount
        interest_added = round(debt_amount * (loan_interest_rate / 12), 2)
        end_debt_amount = round(max(debt_amount + interest_added - monthly_repayment_amount, 0), 2)

        if end_debt_amount <= 0:
            savings_amount = round(monthly_repayment_amount - (debt_amount + interest_added), 2)

        # Cumulative savings calculation
        start_saving_amount = round(savings_amount + end_saving_amount, 2)
        savings_interest = round(start_saving_amount * (savings_growth_rate / 12), 2)
        end_saving_amount = round(start_saving_amount + savings_interest, 2)

        # Debt amount less lump sum variables
        interest_on_debt_less_lump_sum = round(debt_less_lump_sum * (loan_interest_rate / 12), 2)
        end_debt_less_lump_sum = round(
            max(debt_less_lump_sum + interest_on_debt_less_lump_sum - monthly_repayment_amount, 0), 2)

        if end_debt_less_lump_sum <= 0:
            student_loan_savings_from_lump_sum = round(
                monthly_repayment_amount - (debt_less_lump_sum + interest_on_debt_less_lump_sum), 2)

        student_loan_savings_from_lump_sum_start_amount = round(
            student_loan_savings_from_lump_sum + student_loan_savings_from_lump_sum_end_amount, 2)
        student_loan_savings_from_lump_sum_interest = round(
            student_loan_savings_from_lump_sum_start_amount * (savings_growth_rate / 12), 2)
        student_loan_savings_from_lump_sum_end_amount = round(
            student_loan_savings_from_lump_sum_start_amount + student_loan_savings_from_lump_sum_interest, 2)

        lump_sum_interest_added = round(lump_sum_amount * (savings_growth_rate / 12), 2)
        lump_sum_end_amount = round(lump_sum_amount + lump_sum_interest_added, 2)

        lump_sum_saved_debt_not_paid = round(lump_sum_end_amount + end_saving_amount, 2)
        lump_sum_paid_off_student_loan = round(student_loan_savings_from_lump_sum_end_amount, 2)

        lump_sum_saved_debt_not_paid_real_money = round(lump_sum_end_amount + end_saving_amount, 2) / (
                    (1 + inflation_rate) ** (month / 12))
        lump_sum_paid_off_student_loan_real_money = round(student_loan_savings_from_lump_sum_end_amount, 2) / (
                    (1 + inflation_rate) ** (month / 12))

        chart_list.append((year, month, lump_sum_saved_debt_not_paid, lump_sum_paid_off_student_loan,
                           lump_sum_saved_debt_not_paid_real_money, lump_sum_paid_off_student_loan_real_money))

        debt_amount = end_debt_amount
        debt_less_lump_sum = end_debt_less_lump_sum
        lump_sum_amount = lump_sum_end_amount

    return chart_list

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling calculations
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get values from form and convert to correct format
        loan_type = int(request.form['loan_type'])
        annual_salary = float(request.form['annual_salary'])
        inflation_rate = float(request.form['inflation_rate']) / 100  # Convert to decimal
        loan_interest_rate = float(request.form['loan_interest_rate']) / 100  # Convert to decimal
        salary_growth_rate = float(request.form['salary_growth_rate']) / 100  # Convert to decimal
        lump_sum_amount = float(request.form['lump_sum_amount'])
        savings_growth_rate = float(request.form['savings_growth_rate']) / 100  # Convert to decimal
        debt_amount = float(request.form['debt_amount'])
        graduation_year = int(request.form['graduation_year'])

        # Pass the processed values to the calculation function
        chart_data = calculate_chart_data(
            loan_type, annual_salary, inflation_rate, loan_interest_rate,
            salary_growth_rate, debt_amount, lump_sum_amount, savings_growth_rate, graduation_year
        )

        # Generate charts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        months = [item[1] for item in chart_data]
        ax1.plot(months, [item[2] for item in chart_data], label='Lump Sum Saved (Debt Not Paid)', color='blue', linestyle='--')
        ax1.plot(months, [item[3] for item in chart_data], label='Lump Sum Paid Off (Student Loan)', color='green', linestyle='-')
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Amount (£)")
        ax1.set_title("Lump Sum Comparison Over Time")
        ax1.legend()

        ax2.plot(months, [item[4] for item in chart_data], label='Lump Sum Saved (Debt Not Paid, Real Money)', color='purple', linestyle='--')
        ax2.plot(months, [item[5] for item in chart_data], label='Lump Sum Paid Off (Student Loan, Real Money)', color='orange', linestyle='-')
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Amount (£)")
        ax2.set_title("Lump Sum Comparison Over Time (Adjusted for Inflation)")
        ax2.legend()

        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()

        return render_template('result.html', chart_url=chart_url)

    except ValueError as e:
        return f"Invalid input: {e}", 400

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request
from datetime import datetime
import plotly.graph_objs as go
import plotly.io as pio
import plotly.subplots as sp

app = Flask(__name__)

# Calculation function
def calculate_chart_data(
    loan_type: int, annual_salary, inflation_rate,
    salary_growth_rate, debt_amount, lump_sum_amount, savings_growth_rate, graduation_year
):
    annual_salary = float(annual_salary)
    inflation_rate = float(inflation_rate)
    salary_growth_rate = float(salary_growth_rate)
    debt_amount = float(debt_amount)
    lump_sum_amount = float(lump_sum_amount)
    savings_growth_rate = float(savings_growth_rate)
    graduation_year = int(graduation_year)
    current_year = datetime.now().year
    outstanding_years = ((graduation_year + 1) + (30 if loan_type == 2 else 40)) - current_year
    total_months = 12 * outstanding_years

    income_lower = 28470
    income_upper = 51245

    savings_amount = 0
    student_loan_savings_from_lump_sum = 0
    end_saving_amount = 0
    student_loan_savings_from_lump_sum_end_amount = 0
    debt_less_lump_sum = max(debt_amount - lump_sum_amount, 0)
    end_debt_less_lump_sum = debt_less_lump_sum
    chart_list = []
    written_list = []

    for month in range(1, total_months + 1):
        year = (month - 1) // 12 + 1
        year_salary = round(annual_salary * ((1 + salary_growth_rate) ** (year - 1)), 2)

        income_lower_adj = income_lower * ((1 + inflation_rate) ** (year - 1))
        income_upper_adj = income_upper * ((1 + inflation_rate) ** (year - 1))

        if year_salary > income_upper_adj:
            loan_interest_rate = inflation_rate + 0.03
        elif income_lower_adj < year_salary <= income_upper_adj:
            loan_interest_rate = (((year_salary - income_lower_adj) / (income_upper_adj - income_lower_adj)) * 0.03) + inflation_rate
        else:
            loan_interest_rate = inflation_rate

        if loan_type == 2:
            monthly_repayment_amount = round(((year_salary - (27295 * (1 + inflation_rate))) * 0.09) / 12, 2)
        elif loan_type == 5:
            monthly_repayment_amount = round(((year_salary - (25000 * (1 + inflation_rate))) * 0.09) / 12, 2)
        else:
            monthly_repayment_amount = 0

        interest_added = round(debt_amount * (loan_interest_rate / 12), 2)
        end_debt_amount = round(max(debt_amount + interest_added - monthly_repayment_amount, 0), 2)

        if end_debt_amount <= 0:
            savings_amount = round(monthly_repayment_amount - (debt_amount + interest_added), 2)

        start_saving_amount = round(savings_amount + end_saving_amount, 2)
        savings_interest = round(start_saving_amount * (savings_growth_rate / 12), 2)
        end_saving_amount = round(start_saving_amount + savings_interest, 2)

        interest_on_debt_less_lump_sum = round(debt_less_lump_sum * (loan_interest_rate / 12), 2)
        end_debt_less_lump_sum = round(max(debt_less_lump_sum + interest_on_debt_less_lump_sum - monthly_repayment_amount, 0), 2)

        if end_debt_less_lump_sum <= 0:
            student_loan_savings_from_lump_sum = round(monthly_repayment_amount - (debt_less_lump_sum + interest_on_debt_less_lump_sum), 2)

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

        lump_sum_saved_debt_not_paid_real_money = lump_sum_saved_debt_not_paid / ((1 + inflation_rate) ** (month / 12))
        lump_sum_paid_off_student_loan_real_money = lump_sum_paid_off_student_loan / ((1 + inflation_rate) ** (month / 12))

        chart_list.append((year, month, lump_sum_saved_debt_not_paid, lump_sum_paid_off_student_loan,
                           lump_sum_saved_debt_not_paid_real_money, lump_sum_paid_off_student_loan_real_money))

        written_list.append((
            month,
            year_salary,
            loan_interest_rate,
            lump_sum_saved_debt_not_paid,
            lump_sum_paid_off_student_loan,
            lump_sum_saved_debt_not_paid_real_money,
            lump_sum_paid_off_student_loan_real_money,
            end_debt_amount,
            monthly_repayment_amount,
        ))

        debt_amount = end_debt_amount
        debt_less_lump_sum = end_debt_less_lump_sum
        lump_sum_amount = lump_sum_end_amount

    return chart_list, written_list

@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        loan_type = int(request.form['loan_type'])
        annual_salary = float(request.form['annual_salary'])
        inflation_rate = float(request.form['inflation_rate']) / 100
        salary_growth_rate = float(request.form['salary_growth_rate']) / 100
        lump_sum_amount = float(request.form['lump_sum_amount'])
        savings_growth_rate = float(request.form['savings_growth_rate']) / 100
        debt_amount = float(request.form['debt_amount'])
        graduation_year = int(request.form['graduation_year'])

        chart_data, written_list = calculate_chart_data(
            loan_type, annual_salary, inflation_rate,
            salary_growth_rate, debt_amount, lump_sum_amount, savings_growth_rate, graduation_year
        )

        months = [item[1] for item in chart_data]
        y1 = [item[2] for item in chart_data]
        y2 = [item[3] for item in chart_data]
        y3 = [item[4] for item in chart_data]
        y4 = [item[5] for item in chart_data]

        fig = sp.make_subplots(rows=1, cols=2, subplot_titles=(
            "Lump Sum Comparison Over Time",
            "Lump Sum Comparison Over Time (Adjusted for Inflation)"
        ))

        fig.add_trace(go.Scatter(
            x=months, y=y1, mode='lines', name='Lump Sum Saved (Debt Not Paid)', line=dict(color='blue', dash='dash'),
            hovertemplate='Month %{x}<br>Amount: £%{y:.2f}'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=months, y=y2, mode='lines', name='Lump Sum Paid Off (Student Loan)', line=dict(color='green'),
            hovertemplate='Month %{x}<br>Amount: £%{y:.2f}'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=months, y=y3, mode='lines', name='Lump Sum Saved (Real £)', line=dict(color='purple', dash='dash'),
            hovertemplate='Month %{x}<br>Real Amount: £%{y:.2f}'
        ), row=1, col=2)

        fig.add_trace(go.Scatter(
            x=months, y=y4, mode='lines', name='Lump Sum Paid Off (Real £)', line=dict(color='orange'),
            hovertemplate='Month %{x}<br>Real Amount: £%{y:.2f}'
        ), row=1, col=2)

        fig.update_layout(height=600, width=1100, showlegend=True)
        graph_html = pio.to_html(fig, full_html=False)

        # Filter the written_list to get only the relevant months (e.g., every 12th month)
        filtered_written_list = [item for item in written_list if item[0] % 12 == 0]

        # Transpose the filtered data so each inner list represents a row for a metric
        transposed = list(zip(*filtered_written_list))

        # metric_labels are the row titles (first column)
        metric_labels = [
            "Month",
            "Annual Salary (£)",
            "Loan Interest Rate",
            "Invested (£)",
            "Paid off debt (£)",
            "Invested (Real £)",
            "Paid off debt (Real £)",
            "Remaining Debt Value (£)",
            "Monthly Repayment for salary (£)",
        ]

        # Combine metric_labels with transposed data to make the first column
        # Each row = [label] + data_values
        table_data = []
        for label, row_values in zip(metric_labels, transposed):
            table_data.append([label] + list(row_values))

        # Extract column headers from the first row of your data (e.g. the months)
        # Since the first row of table_data is the months row, skip its first element (which is "Month" label)
        column_headers = table_data[0][1:]

        # Now remove the first row from table_data because it’s used as column headers
        # Remaining rows have row titles + data values
        table_data = table_data[1:]

        return render_template(
            'result.html',
            graph_html=graph_html,
            table_data=table_data,
            column_headers=column_headers
        )

    except Exception as e:
        return f"Error: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, send_file
import requests
import csv
import io
from datetime import datetime

app = Flask(__name__)

API_URL = "https://my.zadarma.com/statistics/export/toll"
API_SECRET = "2aUpdhs7Ujd7ZKgD9XA3GaP6A2jxzj1sy7spG79xdVdp4ssa6y"  # Replace with your actual API key


def get_filtered_data(start_date, end_date, filter_numbers=None):
    params = {
        'secret': API_SECRET,
        'start': start_date,
        'end': end_date,
    }

    response = requests.get(API_URL, params=params)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")  # Debug output

    if response.status_code == 200:
        csv_content = response.content.decode('utf-8')
        print(f"CSV Content: {csv_content}")  # Debug output
        filtered_csv = filter_csv(csv_content, filter_numbers)
        return filtered_csv
    else:
        print(f"Error retrieving data: {response.text}")
        return None


def filter_csv(csv_content, filter_numbers):
    csv_reader = csv.reader(io.StringIO(csv_content))
    output = io.StringIO()
    csv_writer = csv.writer(output)

    header = next(csv_reader)
    csv_writer.writerow(header)

    for row in csv_reader:
        csv_writer.writerow(row)

    output.seek(0)
    return output


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        try:
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            start_date = f"{formatted_date}000000"
            end_date = f"{formatted_date}235959"

            filter_numbers = request.form.get('numbers')
            if filter_numbers:
                filter_numbers = filter_numbers.split(',')

            filtered_csv = get_filtered_data(start_date, end_date, filter_numbers)

            if filtered_csv and filtered_csv.getvalue().strip():  # Check if CSV is not empty
                return send_file(
                    io.BytesIO(filtered_csv.getvalue().encode('utf-8')),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'log_{formatted_date}.csv'
                )
            else:
                return "No data available for the selected date.", 200
        except ValueError:
            return "Invalid date format. Please enter the date in YYYY-MM-DD format."

    return '''
    <form method="post">
        <label for="date">Select a date (YYYY-MM-DD):</label>
        <input type="date" id="date" name="date" required>
        <br><br>
        <label for="numbers">Phone numbers (optional, separated by commas):</label>
        <input type="text" id="numbers" name="numbers">
        <br><br>
        <button type="submit">Download log</button>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
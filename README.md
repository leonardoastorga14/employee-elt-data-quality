# Data Quality ELT Pipeline

## Overview
This project demonstrates how to:
1. **Extract** data from a CSV file.
2. **Load** the raw data into a SQLite database.
3. **Transform / Clean** the data either using Python/pandas or SQL, then create a final cleaned table.

## Project Structure
- `data/employee_data.csv`: Source CSV file.
- `approach_1_python_cleaning.py`: Cleans data with Python/pandas.
- `approach_2_sql_cleaning.py`: Cleans data with raw SQL.
- `final_solution.py`: The chosen “best” approach (SQL-based in this example).
- `requirements.txt`: Python dependencies.
- `README.md`: This file.

## How to Run
1. Create a virtual environment (optional, but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows# employee-elt-data-quality

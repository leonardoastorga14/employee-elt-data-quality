# Data Quality ELT Pipeline

## Overview

This project shows how to clean employee data using Python and SQLite. It:
1. Takes data from a CSV file
2. Puts it into a database table called `employee_data_source`
3. Cleans it up and saves it to a new table called `employee_data`

What the cleaning process does:
- Removes duplicate entries
- Makes column formats consistent (Names, Departments, Countries, Dates)
- Fills in missing experience years using math
- Fills in missing performance ratings using AI
- Saves everything to a clean table

## Files in this Repository
- `data/`
  - `employee_data_source.csv` (raw data)
- `final_solution.py` (main cleaning script)
- `README.md` (this file)

## Requirements
- Python 3.8 or newer
- Required packages:
  - pandas
  - numpy
  - scikit-learn
  - sqlite3

## Setup Instructions
1. **Get the Code**
   ```bash
   git clone https://github.com/leonardoastorga14/employee-elt-data-quality.git
   cd data-quality-pipeline
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate it (choose one):
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

3. **Run the Pipeline**
   ```bash
   python final_solution.py
   ```

## How it Works

The script does these things in order:
1. Connects to a SQLite database
2. Reads the CSV file into a raw table
3. Cleans the data:
   - Fixes name formats
   - Standardizes department names
   - Makes dates consistent
   - Fixes country names
   - Predicts missing experience years
   - Predicts missing performance ratings
4. Saves clean data to a new table

## Output

After running the script:
- Raw data will be in the `employee_data_source` table
- Clean data will be in the `employee_data` table

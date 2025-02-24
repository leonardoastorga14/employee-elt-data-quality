# Data Quality ELT Pipeline

## Overview

This project demonstrates how to perform a complete **ELT (Extract, Load, Transform)** pipeline for employee data using **SQLite** and **Python**. The data is:
1. **Extracted** from a CSV file.
2. **Loaded** *as-is* into a raw table (`employee_data_source`) in the database.
3. **Transformed & Cleaned** (using Python, Pandas, and scikit-learn) before being saved into a final table (`employee_data`).

Key data quality tasks include:
- Removing duplicates
- Standardizing columns (Name, Department, Country, Date of Joining)
- Handling missing values for **Years of Experience** (predicted via linear regression)
- Handling missing values for **Performance Rating** (predicted via a random forest classifier)
- Ensuring the final data is stored in a new table named `employee_data`

## Project Structure
- `data/employee_data_source.csv`  
  *(Your raw CSV file.  Update the path in `final_solution.py` if yours is different.)*
- `final_solution.py`  
  *The main Python script that connects to the SQLite database, loads the raw data, cleans it, and saves the cleaned table.*
- `README.md`  
  *This file, describing the project setup and usage.*

## Setup Instructions
1. **Clone or Download** this repository to your local machine.
2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows

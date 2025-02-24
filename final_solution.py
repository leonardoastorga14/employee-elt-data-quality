import sqlite3
import pandas as pd
import os
import numpy as np
from datetime import datetime

# scikit-learn imports for the predictive approach
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

DB_NAME = "employees.db"
CSV_PATH = os.path.join("data", "employee_data_source.csv")


def create_connection(db_file):
    """
    Connect to the SQLite database file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")
    except sqlite3.Error as e:
        print(e)
    return conn


def load_raw_data_to_db(conn, csv_path):
    """
    Step 1: Read CSV file and put it into database table 'employee_data_source'
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Overwrite if the table already exists:
    df.to_sql("employee_data_source", conn, if_exists="replace", index=False)
    print("Raw data loaded into 'employee_data_source' table.")


def clean_data_in_db(conn):
    """
    Step 2: Clean up the data:
    - Get data from employee_data_source table
    - Remove duplicates
    - Fix column formats
    - Fill in missing experience years
    - Fill in missing ratings
    - Save clean data to employee_data table
    """
    # Get data from table
    df = pd.read_sql_query("SELECT * FROM employee_data_source", conn)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Fix column formats:

    # Fix names (capitalize properly)
    def standardize_name(fullname):
        if pd.isna(fullname) or not str(fullname).strip():
            return "Unknown Name"
        parts = str(fullname).split()
        # Capitalize each chunk
        parts = [p.capitalize() for p in parts]
        return " ".join(parts)

    df["Name"] = df["Name"].apply(standardize_name)

    # Fix department names (make them consistent)
    department_map = {
        "h r": "HR",
        "hr": "HR",
        "cust support": "Customer Support",
        "customer support": "Customer Support",
        "it": "IT",
        "i t": "IT",
        "fin": "Finance",
        "finance": "Finance",
        "marketing": "Marketing",
        "sales": "Sales",
        "legal": "Legal",
        "logistics": "Logistics",
        "operations": "Operations",
        "unknown": "Unknown"
    }

    def standardize_department(dept):
        if pd.isna(dept) or not str(dept).strip():
            return "Unknown"
        d = str(dept).strip().lower()
        return department_map.get(d, d.title())  # fallback: "Fin" => "Fin" => "Fin".title() => "Fin"

    df["Department"] = df["Department"].apply(standardize_department)

    # Fix dates (make them YYYY-MM-DD format)
    def standardize_date(d):
        try:
            return pd.to_datetime(d).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            # If date is invalid, set to None
            return None
    
    df["Date of Joining"] = df["Date of Joining"].apply(standardize_date)

    # Fix country names (capitalize properly)
    def standardize_country(c):
        if pd.isna(c) or not str(c).strip():
            return "Unknown"
        c = str(c).strip().lower()
        return c.capitalize()

    df["Country"] = df["Country"].apply(standardize_country)

    # Predict missing experience years using join date
    # Convert dates to numbers we can use
    df["doj_numeric"] = pd.to_datetime(df["Date of Joining"], errors="coerce").astype("int64") // 10**9


    train_mask = df["doj_numeric"].notna() & df["Years of Experience"].notna()
    train_data = df[train_mask]

    if not train_data.empty and train_data["Years of Experience"].nunique() > 1:
        from sklearn.linear_model import LinearRegression
        linreg = LinearRegression()

        X_train = train_data[["doj_numeric"]]
        y_train = train_data["Years of Experience"]

        linreg.fit(X_train, y_train)

        # Predict for rows that have missing Years of Experience but valid date
        missing_mask = df["Years of Experience"].isna() & df["doj_numeric"].notna()
        df.loc[missing_mask, "Years of Experience"] = linreg.predict(
            df.loc[missing_mask, ["doj_numeric"]]
        ).round()

    # If any Years of Experience remain missing, default to 0
    df["Years of Experience"] = df["Years of Experience"].fillna(0)

    # Predict missing performance ratings
    # 0 = Low, 1 = Average, 2 = High, 3 = Top
    rating_map = {
        "Low Performers": 0,
        "Average Performers": 1,
        "High Performers": 2,
        "Top Performers": 3
    }

    # Reverse map for final predictions:
    rating_map_reverse = {v: k for k, v in rating_map.items()}

    # We'll create a new column "Rating Encoded"
    df["Rating Encoded"] = df["Performance Rating"].map(rating_map)

    # STEP B: Build a dataset for training (rows with known rating)
    train_mask_rating = df["Rating Encoded"].notna()
    train_data_rating = df[train_mask_rating].copy()

    # If there's enough variety in the training set, we'll do classification
    if not train_data_rating.empty and train_data_rating["Rating Encoded"].nunique() > 1:
        
        # Features: years_of_experience, salary, department, country, date_of_joining
        # Convert date_of_joining numeric
        train_data_rating["doj_numeric"] = pd.to_datetime(train_data_rating["Date of Joining"], errors="coerce").astype("int64") // 10**9

        # For department and country, do label encoding (or one-hot, if you prefer).
        dept_encoder = LabelEncoder()
        country_encoder = LabelEncoder()

        train_data_rating["dept_enc"] = dept_encoder.fit_transform(train_data_rating["Department"])
        train_data_rating["country_enc"] = country_encoder.fit_transform(train_data_rating["Country"])

        # Features
        X = train_data_rating[["Years of Experience", "Salary", "doj_numeric", "dept_enc", "country_enc"]]
        y = train_data_rating["Rating Encoded"]

        # Train a random forest classifier (could choose any classifier)
        rfc = RandomForestClassifier(n_estimators=100, random_state=42)
        rfc.fit(X, y)

        # STEP C: For rows with missing performance rating, predict
        missing_mask_rating = df["Rating Encoded"].isna()

        if missing_mask_rating.any():
            df.loc[missing_mask_rating, "doj_numeric"] = (
                pd.to_datetime(df.loc[missing_mask_rating, "Date of Joining"], errors="coerce").astype("int64") // 10**9
            )

            df.loc[missing_mask_rating, "dept_enc"] = dept_encoder.transform(df.loc[missing_mask_rating, "Department"])
            df.loc[missing_mask_rating, "country_enc"] = country_encoder.transform(df.loc[missing_mask_rating, "Country"])

            X_missing = df.loc[missing_mask_rating, ["Years of Experience", "Salary", "doj_numeric", "dept_enc", "country_enc"]]
            preds = rfc.predict(X_missing)
            df.loc[missing_mask_rating, "Rating Encoded"] = preds

        df["Performance Rating"] = df["Rating Encoded"].map(rating_map_reverse)

    else:
        df["Performance Rating"] = df["Performance Rating"].fillna("Average Performers")

    df.drop(columns=["Rating Encoded", "dept_enc", "country_enc", "doj_numeric"], errors="ignore", inplace=True)

    # Save clean data to new table
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS employee_data;")
    conn.commit()

    df.to_sql("employee_data", conn, if_exists="replace", index=False)
    print("Cleaning done. Clean data saved to 'employee_data' table.")


def main():
    # Connect to database and run the cleaning process
    conn = create_connection(DB_NAME)
    if conn:
        # Step 1: Put CSV data into database
        load_raw_data_to_db(conn, CSV_PATH)

        # Step 2: Clean the data
        clean_data_in_db(conn)

        conn.close()


if __name__ == "__main__":
    main()
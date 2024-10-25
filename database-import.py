import pandas as pd
import os
import dotenv
from sqlalchemy import create_engine


# Load Excel file
sales_sheet = pd.read_excel("data\data.xlsx", sheet_name=None)

dotenv.load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


# Create MySQL connection
engine = create_engine(
    f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}"
)

# Write data to MySQL
for table, df in sales_sheet.items():

    print(f"<------------------{table} ------------------>\n\n", df, "\n\n")
    df.to_sql(table.lower(), con=engine, if_exists="replace", index=False)

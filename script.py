import pdfplumber
import requests
import sqlite3
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Step 1: Download the PDF
def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded PDF to {save_path}")

# Step 2: Extract Data from PDF
def extract_data_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Parse the text to extract relevant data
            # Example parsing (this will depend on the structure of your PDF)
            # Assuming data is in rows and columns format
            lines = text.split('\n')
            for line in lines:
                if 'Watchhouse' in line:  # Adjust the condition based on your PDF structure
                    columns = line.split()
                    watchhouse = columns[0]
                    adults = int(columns[1])
                    children = int(columns[2])
                    data.append({'watchhouse': watchhouse, 'adults': adults, 'children': children})
    return data

# Step 3: Store Data in Database
def store_data_in_db(data, db_path='custody_data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS custody (
                        id INTEGER PRIMARY KEY,
                        watchhouse TEXT,
                        adults INTEGER,
                        children INTEGER,
                        date TEXT)''')
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    for record in data:
        cursor.execute('''INSERT INTO custody (watchhouse, adults, children, date)
                          VALUES (?, ?, ?, ?)''', (record['watchhouse'], record['adults'], record['children'], date))
    
    conn.commit()
    conn.close()

# Step 4: Update Visualizations
def fetch_data_from_db(db_path='custody_data.db'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM custody', conn)
    conn.close()
    return df

def create_visualizations(df):
    # Group data by date and watchhouse
    grouped = df.groupby(['date', 'watchhouse']).sum().reset_index()
    
    # Create visualizations
    # Example: Line plot showing changes over time for a specific watchhouse
    watchhouse_data = grouped[grouped['watchhouse'] == 'BRISBANE WATCHHOUSE']
    plt.plot(watchhouse_data['date'], watchhouse_data['adults'], label='Adults')
    plt.plot(watchhouse_data['date'], watchhouse_data['children'], label='Children')
    plt.xlabel('Date')
    plt.ylabel('Number of Persons in Custody')
    plt.title('Custody Changes Over Time at Brisbane Watchhouse')
    plt.legend()
    plt.show()

# Main Function to Run the Script
def main():
    # URL to the daily PDF
    pdf_url = 'https://open-crime-data.s3.ap-southeast-2.amazonaws.com/Crime%20Statistics/Persons%20Currently%20In%20Watchhouse%20Custody.pdf'
    # Path to save the downloaded PDF
    pdf_path = 'daily_watchhouse_report.pdf'
    
    # Download the PDF
    download_pdf(pdf_url, pdf_path)
    
    # Extract data from the PDF
    data = extract_data_from_pdf(pdf_path)
    
    # Store data in the database
    store_data_in_db(data)
    
    # Fetch data from the database
    df = fetch_data_from_db()
    
    # Create visualizations
    create_visualizations(df)

# Run the main function
if __name__ == "__main__":
    main()

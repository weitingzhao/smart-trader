import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pytz import timezone

CHARTMILL_FILE_BASE_URL = "http://152.32.172.45:5102/chartmill/sepa/"

def fetch_dataset(date=None, file_pattern=None):
    # Step 1: Handle date input and set default timezone to Chicago
    if date is None:
        chicago_time = datetime.now(timezone('America/Chicago'))
        date = chicago_time.strftime('%Y-%m-%d')

    base_url = f"{CHARTMILL_FILE_BASE_URL}/{date}"

    try:
        response = requests.get(base_url)
        if response.status_code == 404:
            return None

        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML content: {e}")
        return None

    # Step 2: Parse HTML to find the file name
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    csv_file_name = None
    for link in links:
        href = link['href']
        if file_pattern in href:
            csv_file_name = href
            break

    if not csv_file_name:
        print("No matching file found.")
        return None

    # Step 3: Fetch the CSV file content
    csv_url = f"{base_url}/{csv_file_name}"
    try:
        csv_response = requests.get(csv_url)
        csv_response.raise_for_status()
        csv_content = csv_response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSV file: {e}")
        return None

    # Step 4: Load CSV into a DataFrame
    try:
        from io import StringIO
        dataset = pd.read_csv(StringIO(csv_content))
        return dataset
    except Exception as e:
        print(f"Error loading CSV into DataFrame: {e}")
        return None

# Example usage
if __name__ == "__main__":
    date = "2024-12-10"
    file_pattern = "SEPAQ_ALL_chartmill_export_"
    dataset = fetch_dataset(date, file_pattern)
    if dataset is not None:
        print(dataset.head())
    else:
        print("Dataset could not be fetched.")

import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from datetime import datetime
from send_pdf import send_pdf_to_telegram
import asyncio


# Headers to mimic a browser request (to avoid being blocked)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

domain = "https://disclosures-clerk.house.gov/"


def connect_db() -> tuple:  # Return a tuple of connection and cursor
    """Connect to or create a SQLite database for tracking filings."""
    conn = sqlite3.connect("pelosi_filings.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS filings 
                      (id TEXT PRIMARY KEY, date TEXT, url TEXT, downloaded INTEGER)''')
    conn.commit()
    return conn, cursor


def search_pelosi_filings(year=2025) -> list:  # return a list of dictionaries
    """
    Search for Pelosi's financial disclosures for a given year on the House Clerk site.
    Returns a list of dictionaries with filing details (id, date, url).
    """
    url = f"{domain}FinancialDisclosure/ViewMemberSearchResult"
    payload = {
        'lastName': 'pelosi',
        'filingYear': str(year)
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(
                f"Failed to retrieve data. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        filings = []
        # Select all table rows in the library-table class
        rows = soup.select('table.library-table tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 4:  # Ensure we have all columns (Name, Office, Filing Year, Filing)
                # Extract PDF URL from the link in the Name column
                pdf_link = cells[0].find(
                    'a')['href'] if cells[0].find('a') else None
                if pdf_link:
                    if not pdf_link.startswith('http'):
                        pdf_link = f"{domain}{pdf_link}"
                    # Generate a unique ID (e.g., from the PDF filename or URL)
                    filing_id = pdf_link.split('/')[-1].split('.')[0]
                    # Extract filing date (assuming it's part of the "Filing" or derived; here, use a placeholder)
                    filing_date = cells[3].text.strip(
                    ) if cells[3].text.strip() else "unknown"
                    filings.append({
                        'id': filing_id,
                        'date': filing_date,
                        'url': pdf_link
                    })
        return filings

    except Exception as e:
        print(f"Error searching filings: {e}")
        return []


def download_pdf(pdf_url, save_path="./downloads"):
    """
    Download a PDF from a given URL and save it to a local directory.
    Returns the filename if successful, None otherwise.
    """
    try:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        response = requests.get(pdf_url, stream=True, headers=headers)
        if response.status_code == 200:
            pdf_filename = pdf_url.split(
                '/')[-1] or f"pelosi_filing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path = os.path.join(save_path, pdf_filename)

            with open(file_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            asyncio.run(send_pdf_to_telegram(file_path, pdf_filename))
            return pdf_filename
        else:
            print(
                f"Failed to download PDF from {pdf_url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


def check_and_download_new_filings() -> list:  # Return a list of filenames
    """Check for new filings, compare with stored data, and download new PDFs."""
    conn, cursor = connect_db()

    # Search for current filings
    current_filings = search_pelosi_filings(year=2025)
    pdf_filenames = []

    for filing in current_filings:
        # Check if this filing is already in the database
        cursor.execute("SELECT id FROM filings WHERE id = ?", (filing['id'],))
        if not cursor.fetchone():
            # New filing found - download the PDF
            print(
                f"New filing detected: {filing['id']} on {filing['date']} at {filing['url']}")
            pdf_filename = download_pdf(filing['url'])
            if pdf_filename:
                pdf_filenames += [pdf_filename]
                # Store the new filing in the database
                cursor.execute("INSERT INTO filings (id, date, url, downloaded) VALUES (?, ?, ?, ?)",
                               (filing['id'], filing['date'], filing['url'], 1))
                conn.commit()
                print(f"Downloaded and saved as: {pdf_filename}")
            else:
                print(f"Failed to download PDF for filing {filing['id']}")

    conn.close()
    return pdf_filenames

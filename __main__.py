from fetch_filing import check_and_download_new_filings

import time
from datetime import datetime


def main():
    """Run the script periodically to check for new filings."""
    while True:
        print(f"Checking for new Pelosi filings at {datetime.now()}")
        check_and_download_new_filings()
        # Check every 24 hours (86400 seconds)
        time.sleep(86400)


if __name__ == "__main__":
    # For testing, you can run it once instead of in a loop
    # pdf_filenames = check_and_download_new_filings()
    # Uncomment the following to run continuously:
    main()

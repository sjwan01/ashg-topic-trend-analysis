import os
import sys

sys.path.append(os.path.abspath(os.path.join("..")))
from src import *

# Define constants for paths and URLs
SOURCER_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER_NAME = "pdf"
PDF_FOLDER_PATH = os.path.join(SOURCER_DIR, PDF_FOLDER_NAME)
URL = "https://www.ashg.org/meetings/future-past/abstract-archive/"
START_YEAR = 2013
END_YEAR = 2023
EXCLUDE_YEAR = 2020

# Ensure the PDF folder exists
ensure_folder_exists(PDF_FOLDER_PATH)
os.chdir(PDF_FOLDER_PATH)

# Fetch and parse the abstract archive page
if soup := fetch_and_parse_url(URL):
    # Find all <li> elements under the 'entry-content' div
    li_blocks = soup.find("div", "entry-content").find("ul").find_all("li")
    for li in li_blocks:
        # Extract the year from the <strong> tag and filter based on criteria
        year = int(li.strong.text.strip().split(",")[0])
        if START_YEAR <= year <= END_YEAR and year != EXCLUDE_YEAR:
            # Find all <a> elements within the current <li> block
            a_blocks = li.find_all("a")
            for a in a_blocks:
                # Download the file if 'Interactive Search' is not in the link text
                if "Interactive Search" not in a.text:
                    download_file(a["href"], PDF_FOLDER_PATH)

import requests
import os
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SOURCER_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER_NAME = 'pdf'
PDF_FOLDER_PATH = os.path.join(SOURCER_DIR, PDF_FOLDER_NAME)
URL = 'https://www.ashg.org/meetings/future-past/abstract-archive/'
START_YEAR = 2013
END_YEAR = 2023
EXCLUDE_YEAR = 2020

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f'Created folder: {folder_path}')
    else:
        logging.info(f'Folder already exists: {folder_path}')

def fetch_and_parse_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logging.error(f'Error fetching URL {url}: {e}')
        return None

def download_file(link, folder_path):
    filename = os.path.join(folder_path, link.split('/')[-1])
    if os.path.exists(filename):
        logging.info(f'{filename} already exists in {folder_path}')
        return
    try:
        file_response = requests.get(link)
        file_response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(file_response.content)
        logging.info(f'Successfully downloaded {filename}')
    except requests.RequestException as e:
        logging.error(f'Error downloading {link}: {e}')

def main():
    ensure_folder_exists(PDF_FOLDER_PATH)
    os.chdir(PDF_FOLDER_PATH)

    soup = fetch_and_parse_url(URL)
    if soup is None:
        return

    li_blocks = soup.find('div', 'entry-content').find('ul').find_all('li')

    for li in li_blocks:
        year = int(li.strong.text.strip().split(',')[0])
        if START_YEAR <= year <= END_YEAR and year != EXCLUDE_YEAR:
            a_blocks = li.find_all('a')
            for a in a_blocks:
                if 'Interactive Search' not in a.text:
                    download_file(a['href'], PDF_FOLDER_PATH)

main()
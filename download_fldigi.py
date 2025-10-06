import requests
import logging

logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed output
    format='%(asctime)s %(levelname)s %(message)s',
)

logging.info("Script started.")

def get_latest_version_of_fldigi():
    logging.info("Getting latest version of fldigi...")
    url = "https://sourceforge.net/projects/fldigi/files/fldigi/"
    response = requests.get(url)
    logging.info(f"Fetched fldigi page with status code: {response.status_code}")
    if response.status_code != 200:
        logging.error("Failed to fetch the fldigi webpage")
        raise Exception("Failed to fetch the webpage")
    
    # Extract version numbers from the page content
    versions = []
    for line in response.text.splitlines():
        if 'href="' in line and 'fldigi-' in line:
            start = line.find('fldigi-') + len('fldigi-')
            end = line.find('.tar.gz', start)
            if end != -1:
                version = line[start:end]
                versions.append(version)
    
    logging.info(f"Found fldigi versions: {versions}")
    if not versions:
        logging.error("No fldigi versions found on the webpage")
        raise Exception("No versions found on the webpage")
    
    # Sort versions and return the latest one
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    logging.info(f"Latest fldigi version: {versions[-1]}")
    return versions[-1]


def get_latest_version_of_flrig():
    logging.info("Getting latest version of flrig...")
    url = "https://sourceforge.net/projects/fldigi/files/flrig/"
    response = requests.get(url)
    logging.info(f"Fetched flrig page with status code: {response.status_code}")
    if response.status_code != 200:
        logging.error("Failed to fetch the flrig webpage")
        raise Exception("Failed to fetch the webpage")
    
    # Extract version numbers from the page content
    versions = []
    for line in response.text.splitlines():
        if 'href="' in line and 'flrig-' in line:
            start = line.find('flrig-') + len('flrig-')
            end = line.find('.tar.gz', start)
            if end != -1:
                version = line[start:end]
                versions.append(version)
    
    logging.info(f"Found flrig versions: {versions}")
    if not versions:
        logging.error("No flrig versions found on the webpage")
        raise Exception("No versions found on the webpage")
    
    # Sort versions and return the latest one
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    logging.info(f"Latest flrig version: {versions[-1]}")
    return versions[-1]


def download_fldigi(version):
    base_url = "https://www.w1hkj.org/files/fldigi/"
    file_name = f"fldigi-{version}.tar.gz"
    download_url = f"{base_url}/{file_name}"
    logging.info(f"Downloading fldigi from {download_url}")
    response = requests.get(download_url, stream=True)
    logging.info(f"Download response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error("Failed to download the fldigi file")
        raise Exception("Failed to download the file")
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    logging.info(f"Downloaded fldigi file: {file_name}")

def download_flrig(version):
    base_url = "https://www.w1hkj.org/files/flrig/"
    file_name = f"flrig-{version}.tar.gz"
    download_url = f"{base_url}/{file_name}"
    logging.info(f"Downloading flrig from {download_url}")
    response = requests.get(download_url, stream=True)
    logging.info(f"Download response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error("Failed to download the flrig file")
        raise Exception("Failed to download the file")
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    logging.info(f"Downloaded flrig file: {file_name}")

if __name__ == "__main__":
    try:
        latest_version = get_latest_version_of_fldigi()
        download_fldigi(latest_version)
    except Exception as e:
        logging.error(f"Error with fldigi: {e}", exc_info=True)

    try:
        latest_version_flrig = get_latest_version_of_flrig()
        download_flrig(latest_version_flrig)
    except Exception as e:
        logging.error(f"Error with flrig: {e}", exc_info=True)

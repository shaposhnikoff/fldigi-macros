import requests

def get_latest_version_of_fldigi():
    url = "https://sourceforge.net/projects/fldigi/files/fldigi/"
    response = requests.get(url)
    if response.status_code != 200:
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
    
    if not versions:
        raise Exception("No versions found on the webpage")
    
    # Sort versions and return the latest one
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    print(url)
    print(versions)
    return versions[-1]


def get_latest_version_of_flrig():
    url = "https://sourceforge.net/projects/fldigi/files/flrig/"
    response = requests.get(url)
    if response.status_code != 200:
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
    
    if not versions:
        raise Exception("No versions found on the webpage")
    
    # Sort versions and return the latest one
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    print(url)
    print(versions)
    return versions[-1]


def download_fldigi(version):
    base_url = "https://www.w1hkj.org/files/fldigi/"
    file_name = f"fldigi-{version}.tar.gz"
    download_url = f"{base_url}/{file_name}"
    print(f"Downloading from {download_url}")
    response = requests.get(download_url, stream=True)
    if response.status_code != 200:
        raise Exception("Failed to download the file")
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print(f"Downloaded {file_name}")

def download_flrig(version):
    base_url = "https://www.w1hkj.org/files/flrig/"
    file_name = f"flrig-{version}.tar.gz"
    download_url = f"{base_url}/{file_name}"
    print(f"Downloading from {download_url}")
    response = requests.get(download_url, stream=True)
    if response.status_code != 200:
        raise Exception("Failed to download the file")
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print(f"Downloaded {file_name}")

if __name__ == "__main__":
    latest_version = get_latest_version_of_fldigi()
    download_fldigi(latest_version)

    latest_version_flrig = get_latest_version_of_flrig()
    download_flrig(latest_version_flrig)

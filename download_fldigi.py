import requests
import logging
import subprocess
import sys
import tarfile
import os

# Set environment variable BUILD=true
os.environ["BUILD"] = "true"

# software = {
#     "fldigi": "https://www.w1hkj.org/files/fldigi/",
#     "flrig": "https://www.w1hkj.org/files/flrig/",
#     "flmsg": "https://www.w1hkj.org/files/flmsg/",
#     "flamp": "https://www.w1hkj.org/files/flamp/",
#     "flwrap": "https://www.w1hkj.org/files/flwrap/",
#     "flnet": "https://www.w1hkj.org/files/flnet/",
#     "flarq": "https://www.w1hkj.org/files/flarq/",
#     "flcluster": "https://www.w1hkj.org/files/flcluster/",
#     "flxmlrpc": "https://www.w1hkj.org/files/flxmlrpc/",
#     "flrig-doc": "https://www.w1hkj.org/files/flrig-doc/",
# }


software = {

    "flrig": "https://www.w1hkj.org/files/flrig/",

}





logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed output
    format='%(asctime)s %(levelname)s %(message)s',
)

logging.info("Script started.")

def install_build_dependencies():
    logging.info("Installing build dependencies via apt...")
    packages = [
        "build-essential", "libfltk1.3-dev", "libsamplerate0-dev", "portaudio19-dev",
        "libsndfile1-dev", "libxft-dev", "libxinerama-dev", "libxcursor-dev",
        "libpulse-dev", "pavucontrol", "libusb-1.0-0-dev", "libudev-dev"
    ]
    cmd = ["sudo", "apt", "-y", "install"] + packages
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info("Dependency install output:\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("Error installing dependencies:\n" + e.stderr)
        sys.exit(1)

def configure_and_build(source_dir=".",appname="fldigi"):
    logging.info(f"Configuring and building in {source_dir} ...")
    try:
        # Configure first
        configure_cmd = [
            "./configure",
            "--prefix=/opt/" + appname,
            "--enable-optimizations=x86-64",
            "--enable-debug"
        ]
        result = subprocess.run(configure_cmd, check=True, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info("Configure output:\n" + result.stdout)

        # Clean previous builds (now that Makefile exists)
        try:
            subprocess.run(["make", "clean"], check=True, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logging.info("make clean successful.")
        except subprocess.CalledProcessError:
            logging.info("make clean skipped (no existing build)")

        # Build
        result = subprocess.run(["make", "-j4"], check=True, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info("Build output:\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("Configure/build error:\n" + e.stderr)
        sys.exit(1)

def install_with_make(source_dir=".", appname="fldigi"):
    """Install the application using make install.
    
    Args:
        source_dir: Directory containing the built application
        appname: Name of the application
    """
    logging.info(f"Installing {appname} with make install in {source_dir}")
    try:
        result = subprocess.run(
            ["sudo", "make", "install"], 
            check=True, 
            cwd=source_dir, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        logging.info(f"Make install output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Make install failed: {e.stderr}")
        raise

def create_deb_package(source_dir=".", appname="fldigi", version="1.0.0", release="1", install=True):
    """Create a DEB package using checkinstall.
    
    Args:
        source_dir: Directory containing the built application
        appname: Name of the application
        version: Version string
        release: Release number
        install: Whether to install the package after creation
    
    Returns:
        str: Path to the created DEB package
    """
    logging.info(f"Creating DEB package for {appname} version {version} in {source_dir}")
    
    # First check if checkinstall is installed
    try:
        subprocess.run(["which", "checkinstall"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logging.error("checkinstall not found. Installing...")
        try:
            subprocess.run(["sudo", "apt", "-y", "install", "checkinstall"], check=True)
            logging.info("checkinstall installed successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install checkinstall: {e}")
            raise
    
    # Install first using make install (required for checkinstall to work)
    try:
        install_with_make(source_dir, appname)
    except subprocess.CalledProcessError as e:
        logging.error(f"Make install failed, trying alternative approach: {e}")
        # Try creating package without prior installation
        pass
    
    # Build checkinstall command with sudo
    checkinstall_cmd = [
        "sudo", "checkinstall",
        f"--pkgname={appname}",
        f"--pkgversion={version}",
        f"--pkgrelease={release}",
        "--backup=no",
        "--deldoc=yes", 
        "--deldesc=yes",
        "--delspec=yes",
        "--default",
        f"--install={'yes' if install else 'no'}",
        "make", "install"  # Explicitly specify the install command
    ]
    
    try:
        logging.info(f"Running checkinstall command: {' '.join(checkinstall_cmd)}")
        result = subprocess.run(
            checkinstall_cmd, 
            check=True, 
            cwd=source_dir, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            input="\n"  # Auto-confirm any prompts
        )
        logging.info("Checkinstall output:\n" + result.stdout)
        
        # Find the created DEB file
        deb_pattern = f"{appname}_{version}-{release}_*.deb"
        deb_files = []
        for file in os.listdir(source_dir):
            if file.startswith(f"{appname}_{version}-{release}") and file.endswith('.deb'):
                deb_files.append(os.path.join(source_dir, file))
        
        if deb_files:
            deb_file = deb_files[0]
            logging.info(f"DEB package created: {deb_file}")
            return deb_file
        else:
            logging.warning("DEB file not found in expected location")
            return None
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Checkinstall failed: {e.stderr}")
        # Try alternative: just install normally and skip package creation
        logging.info("Falling back to regular make install without package creation")
        try:
            install_with_make(source_dir, appname)
            logging.info(f"{appname} installed successfully via make install")
            return None
        except subprocess.CalledProcessError as install_error:
            logging.error(f"Both checkinstall and make install failed: {install_error}")
            raise

def extract_archive(filename, dest_dir):
    logging.info(f"Extracting {filename} to {dest_dir} ...")
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall(path=dest_dir)
        logging.info(f"Extraction complete: {filename} -> {dest_dir}")
    except Exception as e:
        logging.error(f"Failed to extract archive {filename}: {e}", exc_info=True)
        sys.exit(1)

def get_latest_version_of_app(app_name):
    logging.info(f"Getting latest version of {app_name}...")
    url = software[app_name]
    response = requests.get(url)
    logging.info(f"Fetched {app_name} page with status code: {response.status_code}")
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred for {app_name}: {e}")
        return None
        


    # Extract version numbers from the page content
    versions = []
    for line in response.text.splitlines():
        if 'href="' in line and f'{app_name}-' in line:
            start = line.find(f'{app_name}-') + len(f'{app_name}-')
            end = line.find('.tar.gz', start)
            if end != -1:
                version = line[start:end]
                versions.append(version)

    logging.info(f"Found {app_name} versions: {versions}")
    if not versions:
        logging.error(f"No {app_name} versions found on the webpage")
        raise Exception("No versions found on the webpage")
    
    # Sort versions and return the latest one
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    logging.info(f"Latest {app_name} version: {versions[-1]}")
    return versions[-1]

# def get_latest_version_of_flrig():
#     logging.info("Getting latest version of flrig...")
#     url = "https://sourceforge.net/projects/fldigi/files/flrig/"
#     response = requests.get(url)
#     logging.info(f"Fetched flrig page with status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error("Failed to fetch the flrig webpage")
#         raise Exception("Failed to fetch the webpage")
    
#     # Extract version numbers from the page content
#     versions = []
#     for line in response.text.splitlines():
#         if 'href="' in line and 'flrig-' in line:
#             start = line.find('flrig-') + len('flrig-')
#             end = line.find('.tar.gz', start)
#             if end != -1:
#                 version = line[start:end]
#                 versions.append(version)
    
#     logging.info(f"Found flrig versions: {versions}")
#     if not versions:
#         logging.error("No flrig versions found on the webpage")
#         raise Exception("No versions found on the webpage")
    
#     # Sort versions and return the latest one
#     versions.sort(key=lambda s: list(map(int, s.split('.'))))
#     logging.info(f"Latest flrig version: {versions[-1]}")
#     return versions[-1]

def download_program(program_name, version, base_url=None):
    """Generic function to download a program from the software dictionary.
    
    Args:
        program_name: Name of the program (e.g., 'fldigi', 'flrig')
        version: Version string of the program
        base_url: Optional base URL. If not provided, uses the software dict
    
    Returns:
        str: Downloaded file name
    """
    if base_url is None:
        if program_name not in software:
            raise ValueError(f"Unknown program: {program_name}")
        base_url = software[program_name]
    
    file_name = f"{program_name}-{version}.tar.gz"
    download_url = f"{base_url}{file_name}"
    logging.info(f"Downloading {program_name} from {download_url}")
    response = requests.get(download_url, stream=True)
    logging.info(f"Download response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Failed to download the {program_name} file")
        raise Exception(f"Failed to download the file")
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    logging.info(f"Downloaded {program_name} file: {file_name}")
    return file_name

def download_fldigi(version):
    return download_program("fldigi", version)

def download_flrig(version):
    return download_program("flrig", version)

def download_all_programs(programs_dict, get_version_func=None):
    """Iterate over the programs dictionary and download each program.
    
    Args:
        programs_dict: Dictionary with program names as keys and URLs as values
        get_version_func: Optional function to get version for a program.
                         Should accept program_name as argument and return version string.
    
    Returns:
        dict: Dictionary mapping program names to downloaded file names
    """
    downloaded_files = {}
    for program_name, base_url in programs_dict.items():
        try:
            if get_version_func:
                version = get_version_func(program_name)
            else:
                logging.warning(f"No version function provided for {program_name}, skipping")
                continue
            
            file_name = download_program(program_name, version, base_url)
            downloaded_files[program_name] = file_name
            logging.info(f"Successfully downloaded {program_name}: {file_name}")
        except Exception as e:
            logging.error(f"Error downloading {program_name}: {e}", exc_info=True)
    
    return downloaded_files

if __name__ == "__main__":
    for program, url in software.items():
        logging.info(f"{program}: {url}")
        try:
            version = get_latest_version_of_app(program)
            if version is None:
                logging.warning(f"Skipping {program} - could not get version")
                continue
            
            download_program(program, version, url)
            logging.info(f"Successfully processed {program} version {version}")
            extract_archive(f"{program}-{version}.tar.gz", ".")
            
            # Build the program first
            source_dir = f"{program}-{version}"
            logging.info(f"Building {program} in directory {source_dir}")
            install_build_dependencies()
            configure_and_build(source_dir, program)
            
            # Create DEB package after building (or fall back to regular install)
            try:
                deb_file = create_deb_package(source_dir, program, version, "1", install=False)
                if deb_file:
                    logging.info(f"DEB package created successfully: {deb_file}")
                else:
                    logging.info(f"No DEB package created for {program}, but installation may have succeeded")
            except Exception as pkg_error:
                logging.error(f"Package creation failed for {program}: {pkg_error}")
                # Continue with next program instead of stopping
                continue
    
        except Exception as e:
            logging.error(f"Error processing {program}: {e}")
            continue
    
    # install_build_dependencies()
    # try:
    #     latest_version = get_latest_version_of_app("fldigi")
    #     fldigi_file = 
    #     fldigi_dir = f"fldigi-{latest_version}"
    #     extract_archive(fldigi_file, ".")
    #     # Only run build if BUILD env var is set to "true"
    #     if os.environ.get("BUILD", "").lower() == "true":
    #         configure_and_build(fldigi_dir)
    #     else:
    #         logging.info("Skipping build step because BUILD env var is not true.")
    # except Exception as e:
    #     logging.error(f"Error with fldigi: {e}", exc_info=True)

    # try:
    #     latest_version_flrig = get_latest_version_of_flrig()
    #     flrig_file = download_flrig(latest_version_flrig)
    #     flrig_dir = f"flrig-{latest_version_flrig}"
    #     logging.info(flrig_file)
    #     logging.info(flrig_dir)
    #     extract_archive(flrig_file, ".")
    #     os.chdir(flrig_dir)
    #     # Only run build if BUILD env var is set to "true"
    #     if os.environ.get("BUILD", "").lower() == "true":
    #         configure_and_build(flrig_dir)
    #     else:
    #         logging.info("Skipping build step for flrig because BUILD env var is not true.")
    
    #     # configure_and_build(flrig_dir)  # Uncomment/configure if you want to build flrig
    #     
    #     # Create DEB package after building
    #     deb_file = create_deb_package(flrig_dir, "flrig", latest_version_flrig, "1", install=True)
    #     if deb_file:
    #         logging.info(f"DEB package created successfully: {deb_file}")
    #     else:
    #         logging.error("Failed to create DEB package")
    #
    # except Exception as e:
    #     logging.error(f"Error with flrig: {e}", exc_info=True)

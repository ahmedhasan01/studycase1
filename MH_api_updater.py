import sys
from MH_libraries import subprocess, logging, os

def update_iqoptionapi():
    """Updates the IQ Option API from GitHub."""
    repo_url = "https://github.com/iqoptionapi/iqoptionapi.git"
    package_name = "api-iqoption-faria"

    try:
        logging.info("Checking and updating IQ Option API...")

        # Check if iqoptionapi is installed
        try:
            import api_iqoption_faria
            logging.info(f"{package_name} is installed, checking for updates...")
        except ImportError:
            logging.info(f"{package_name} not found, installing now...")

        # Define package installation path
        package_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", package_name)

        # Clone or update the repository
        if os.path.exists(package_path):
            logging.info("Existing installation found, pulling latest changes...")
            subprocess.run(["git", "-C", package_path, "pull"], check=True)
        else:
            logging.info("Cloning the repository for the first time...")
            subprocess.run(["git", "clone", repo_url, package_path], check=True)

        # Reinstall the package
        logging.info("Installing the updated version...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", package_path], check=True)

        logging.info("IQ Option API updated successfully.")

    except Exception as e:
        logging.error(f"Error updating {package_name}: {e}")

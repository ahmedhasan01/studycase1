import sys
from MH_libraries import subprocess, logging, os

def update_iqoptionapi():
    """Checks if the IQ Option API needs an update, updates if required, and restarts the application."""
    repo_url = "https://github.com/iqoptionapi/iqoptionapi.git"
    package_name = "api-iqoption-faria"
    
    try:
        logging.info("Checking IQ Option API for updates...")
        
        # Define package installation path
        package_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", package_name)
        
        # Check if package exists
        if os.path.exists(package_path):
            logging.info("Existing installation found, checking for updates...")
            result = subprocess.run(["git", "-C", package_path, "fetch"], capture_output=True, text=True)
            status = subprocess.run(["git", "-C", package_path, "status", "-uno"], capture_output=True, text=True)
            
            if "Your branch is behind" in status.stdout:
                logging.info("Update required. Updating now...")
                subprocess.run(["git", "-C", package_path, "pull"], check=True)
            else:
                logging.info("IQ Option API is already up to date.")
                return
        else:
            logging.info("Package not found, cloning for the first time...")
            subprocess.run(["git", "clone", repo_url, package_path], check=True)
        
        # Reinstall the package
        logging.info("Installing the updated version...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", package_path], check=True)
        
        logging.info("IQ Option API updated successfully. Restarting application...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    except Exception as e:
        logging.error(f"Error updating {package_name}: {e}")
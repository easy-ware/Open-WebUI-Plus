import os
import platform
import requests
import json
import shutil
import sys
from pathlib import Path
import logging
from colorama import init, Fore, Style
import time

# Initialize colorama
init()

# Configure logging
class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored logs"""
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    
    FORMATS = {
        logging.DEBUG: Fore.CYAN + format_str + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + format_str + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

# Setup logger
logger = logging.getLogger('cloudflared_downloader')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(ColoredFormatter())
logger.addHandler(ch)

def terminate_script(error_message):
    """Terminate script execution with error message"""
    logger.error(f"Fatal error: {error_message}")
    print(f"{Fore.RED}Terminating script execution{Style.RESET_ALL}")
    sys.exit(1)

def get_system_info():
    """Get detailed system information"""
    try:
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        arch_map = {
            'amd64': 'amd64',
            'x86_64': 'amd64',
            'arm64': 'arm64',
            'aarch64': 'arm64',
            'x86': '386',
            'i386': '386'
        }
        
        system_map = {
            'windows': 'windows',
            'linux': 'linux',
            'darwin': 'darwin'
        }
        
        arch = arch_map.get(machine, machine)
        os_type = system_map.get(system, system)
        
        if not arch or not os_type:
            raise Exception(f"Unsupported system: {system} {machine}")
        
        return os_type, arch
    except Exception as e:
        terminate_script(f"Failed to get system information: {str(e)}")

def get_cloudflared_info():
    """Get latest CloudFlared version and download URL from GitHub releases"""
    try:
        logger.info("Fetching latest CloudFlared release information...")
        
        api_url = "https://api.github.com/repos/cloudflare/cloudflared/releases/latest"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        release_data = response.json()
        version = release_data['tag_name'].replace('v', '')
        
        os_type, arch = get_system_info()
        logger.debug(f"Detected system: {os_type}-{arch}")
        
        # Construct filename based on system
        if os_type == 'windows':
            filename = f'cloudflared-{os_type}-{arch}.exe'
        else:
            filename = f'cloudflared-{os_type}-{arch}'
        
        # Find matching asset URL
        download_url = None
        for asset in release_data['assets']:
            if asset['name'] == filename:
                download_url = asset['browser_download_url']
                break
                
        if not download_url:
            raise Exception(f"No compatible binary found for {os_type}-{arch}")
        
        return version, download_url, filename, os_type, arch
    except requests.exceptions.RequestException as e:
        terminate_script(f"Failed to fetch CloudFlared release info: {str(e)}")
    except Exception as e:
        terminate_script(f"Error getting CloudFlared info: {str(e)}")

def download_cloudflared():
    """Download CloudFlared and manage versions"""
    try:
        # Get system info and create directory structure
        version, download_url, filename, os_type, arch = get_cloudflared_info()
        platform_dir = f"{os_type}-{arch}"
        
        base_dir = Path('driver/cloudflared')
        platform_path = base_dir / platform_dir
        binary_path = platform_path / filename
        
        # First check if binary exists and is executable
        if binary_path.exists() and (platform.system() == 'Windows' or os.access(str(binary_path), os.X_OK)):
            logger.info(f"CloudFlared binary already exists at: {binary_path}")
            return str(binary_path)
        
        try:
            platform_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            terminate_script(f"Failed to create directory structure: {str(e)}")
        
        logger.info(f"Using platform directory: {platform_path}")
        
        # Download new version
        logger.info("Downloading CloudFlared...")
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size for progress
            total_size = int(response.headers.get('content-length', 0))
            
            # Save the binary with progress
            with open(binary_path, 'wb') as f:
                if total_size == 0:
                    shutil.copyfileobj(response.raw, f)
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=8192):
                        downloaded += len(data)
                        f.write(data)
                        done = int(50 * downloaded / total_size)
                        percent = int(100 * downloaded / total_size)
                        print(f"\rDownload progress: [{('=' * done) + (' ' * (50-done))}] {percent}%", end='')
            print()  # New line after progress bar
        except Exception as e:
            # Clean up failed download
            if binary_path.exists():
                try:
                    binary_path.unlink()
                except:
                    pass
            terminate_script(f"Failed to download CloudFlared: {str(e)}")
        
        # Make binary executable on Unix systems
        if platform.system() != 'Windows':
            try:
                binary_path.chmod(0o755)
                logger.info("Set executable permissions")
            except Exception as e:
                terminate_script(f"Failed to set executable permissions: {str(e)}")
        
        # Verify binary exists and is executable
        if not binary_path.exists():
            terminate_script("Binary not found after download")
        
        if not os.access(str(binary_path), os.X_OK) and platform.system() != 'Windows':
            terminate_script("Binary is not executable after setting permissions")
        
        logger.info(f"Successfully downloaded CloudFlared")
        logger.info(f"Binary location: {binary_path}")
        
        return str(binary_path)
        
    except Exception as e:
        terminate_script(f"Error downloading CloudFlared: {str(e)}")
if __name__ == "__main__":
    try:
        path = download_cloudflared()
        logger.info(f"CloudFlared binary path: {path}")
    except Exception as e:
        terminate_script(str(e))
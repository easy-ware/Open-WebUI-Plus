import os
import logging
from colorama import Fore, Style, init
import subprocess
import threading
import re
import time


# Initialize colorama
init(autoreset=True)

def create_directory(path):
    """
    Create a directory and all necessary subdirectories.
    Logs success or error messages.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"{Fore.GREEN}Directory '{path}' created successfully.")
            logging.info(f"Directory '{path}' created successfully.")
        else:
            print(f"{Fore.YELLOW}Directory '{path}' already exists.")
            logging.info(f"Directory '{path}' already exists.")
    except Exception as e:
        print(f"{Fore.RED}Failed to create directory '{path}'. Error: {e}")
        logging.error(f"Failed to create directory '{path}'. Error: {e}")

def make_dir(dir_path, logfile=None):
    """
    Create the target directory and ensure logs directory exists.
    """
    # Set default log file path if not provided
    if logfile is None:
        logfile = os.path.join(os.getcwd(), "logs", "dir_creation", "directory_creation.log")

    # Ensure the logs directory exists
    log_dir = os.path.dirname(logfile)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"{Fore.GREEN}Log directory '{log_dir}' created successfully.")
    else:
        print(f"{Fore.YELLOW}Log directory '{log_dir}' already exists.")

    # Configure logging
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging initialized.")

    # Create the target directory
    create_directory(dir_path)
    print(f"{Style.BRIGHT}Log written to '{logfile}'.")

def tost(text, color="default"):
    """
    Prints the given text in the specified color, with decorative lines before and after.

    Parameters:
        text (str): The text to color and print.
        color (str): The name of the color (default, red, green, yellow, blue, magenta, cyan, white).
    """
    colors = {
        "default": "\033[0m",  # Reset to default
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m"
    }
    
    # Get the color code, default to no color if not found
    color_code = colors.get(color.lower(), colors["default"])
    
    # Print the decorative lines and the colored text
    print("=" * 40)
    print(f"{color_code}{text}{colors['default']}")  # Reset color after printing
    print("=" * 40)



def monitor_output(pipe , message , path):
    """Monitor the process output for the Cloudflare URL"""
    while True:
        line = pipe.readline()
        if not line:
            break
        # Look for trycloudflare.com URL in the output
        url_match = re.search(r'https?://[a-zA-Z0-9-]+\.trycloudflare\.com', line.decode('utf-8', errors='ignore'))
        if url_match:
            print(f"{Fore.MAGENTA}""="*80)
            print(f"{Fore.GREEN}\n{message} : {url_match.group(0)}\n{Fore.GREEN}")
            with open(path , "w") as ms:
              ms.write(url_match.group(0))
            print(f"{Fore.MAGENTA}""="*45)

def run_cloudflare(port , message , path):
    # Command to run cloudflared tunnel
    with open(os.path.join(os.getcwd() , "access" , "cloudflare.txt") , "r") as cl:
        driver = os.path.join(os.getcwd() , cl.read())
    cl.close()
    print(driver)
    command = [
        f'{driver}',
        'tunnel',
        '--url',
        f'localhost:{port}',
        '--protocol',
        'http2'
    ]

    # Start the process in background
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Start monitoring threads for both stdout and stderr
    stdout_thread = threading.Thread(
        target=monitor_output, 
        args=(process.stdout, message, path)
    )
    stderr_thread = threading.Thread(
        target=monitor_output, 
        args=(process.stderr, message, path)
    )


    stdout_thread.daemon = True
    stderr_thread.daemon = True

    stdout_thread.start()
    stderr_thread.start()

    return process

def get_content(path):
    with open(path , "r") as ms:
        return ms.read()
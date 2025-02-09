import util
import os
import tts
import subprocess
import logging
from get_cloudflare import cloudflare
import threading
from flask import Flask, render_template, abort
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys
from jinja2 import TemplateNotFound

# Configure logging for both servers
def setup_logger(name, log_file):
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        os.path.join('logs', log_file),
        maxBytes=10000,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Project dir setup on start
needed_dirs = ["logs", "driver", "driver/cloudflared", "access", "templates"]

def create_struc(dir_list):
    base_path = os.getcwd()
    for s in dir_list:
        path_components = s.split('/')
        full_path = os.path.join(base_path, *path_components)
        util.make_dir(full_path)

# Create Flask apps with shared template folder
template_dir = os.path.abspath(os.path.join(os.getcwd(), "open-webui-plus" , 'templates'))

# TTS app
tts_app = tts.create_app()
tts_app.template_folder = template_dir
tts_logger = setup_logger('tts_server', 'tts_server.log')

# Open-webui-plus app
open_webui_plus_app = Flask("Open-WebUI-Plus", 
                          template_folder=template_dir,
                          static_folder=os.path.join(os.getcwd(), 'static'))
main_logger = setup_logger('main_server', 'main_server.log')

# Add logging to both apps
for handler in tts_logger.handlers:
    tts_app.logger.addHandler(handler)
tts_app.logger.setLevel(logging.INFO)

for handler in main_logger.handlers:
    open_webui_plus_app.logger.addHandler(handler)
open_webui_plus_app.logger.setLevel(logging.INFO)

# TTS app runner
def run_tts(app, port, host="0.0.0.0"):
    util.tost(f"\nStarting TTS server at port:{port}", "green")
    tts_logger.info(f"\nStarting TTS server at http://{host}:{port}")
    util.run_cloudflare(port, "TTS Server Access URL", path=os.path.join(os.getcwd(), "access", "cloudflare_tts_url.txt"))
    app.run(port=port, host=host)

# Download cloudflared
def get_cloudflared():
    cloudflared_driver_path = cloudflare.download_cloudflared()
    with open(os.path.join(os.getcwd(), "access", "cloudflare.txt"), "w") as cl:
        cl.write(cloudflared_driver_path)

# Run main server
def open_web_ui_plus(app, port, host="0.0.0.0"):
    util.tost(f"\nStarting Main server on port:{port}", "green")
    main_logger.info(f"\nStarting Main server at http://{host}:{port}")
    util.run_cloudflare(port, "Main server access:", path=os.path.join(os.getcwd(), "access", "cloudflare_main_url.txt"))
    app.run(port=port, host=host)

route_ui = open_webui_plus_app  # for easy reference

@route_ui.route("/")
def get_tts():
    try:
        with open(os.path.join(os.getcwd(), "access", "cloudflare_tts_url.txt"), "r") as cl:
            url = cl.read().strip()  # Added strip() to remove any whitespace
        
        main_logger.info("TTS endpoint accessed")
        main_logger.debug(f"Template directory: {template_dir}")
        
        return render_template(
            'tts_url.html',
            title='TTS url',
            header_text="Here's Your TTS Url",
            message=f'Just go to the open-webui and in the audio section choose \n openai \n And in creds add \n api key = open-web-ui-plus \n in voice add from \n fast \n normal \n slow \n in voice model choose from models go to this url {url}/v1/models and just save the settings \n Also for other url visit {util.get_content(os.path.join(os.getcwd(), "access", "cloudflare_main_url.txt"))}/access-points',
            url=f'{url}/v1',
            footer_text='open-webui-plus',
            now=datetime
        )
    except TemplateNotFound:
        main_logger.error(f"Template not found: tts_url.html in {template_dir}")
        return f"Error: Template not found. Looking in: {template_dir}", 500
    except Exception as e:
        main_logger.error(f"Error in get_tts: {str(e)}")
        return f"Error: {str(e)}", 500

@route_ui.route("/access-points")
def ac_p():
    urls = [
    {'name': 'Main Server', 'url': f'{util.get_content(os.path.join(os.getcwd(), "access", "cloudflare_main_url.txt"))}', 'status': 'active'},
    {'name': 'TTS Server', 'url': f'{util.get_content(os.path.join(os.getcwd(), "access", "cloudflare_tts_url.txt"))}', 'status': 'active'},
    {'name': 'STT Server', 'url': f'{util.get_content(os.path.join(os.getcwd(), "access", "cloudflare_stt_url.txt"))}', 'status': 'active'},
    {'name': 'Open Web UI Server', 'url': f'{util.get_content(os.path.join(os.getcwd(), "access", "cloudflare_open-webui_url.txt"))}', 'status': 'active'}
      ]

    return render_template("access_points.html" , urls = urls)
# Main server run
if __name__ == "__main__":
    try:
        create_struc(needed_dirs)  # create project structure
        main_logger.info("Created project directory structure")
        main_logger.info(f"Template directory set to: {template_dir}")
        
        get_cloudflared()  # download cloudflared driver
        main_logger.info("Downloaded cloudflared driver")
        
        tts.DatabaseManager.init_db()  # start database tts
        main_logger.info("Initialized TTS database")
        
        tts.CleanupService.start()  # start cleanup service
        main_logger.info("Started cleanup service")
        #start open-webui
        subprocess.Popen("open-webui serve" , shell = True)
        main_logger.info("Started open-webui")
        util.tost("Access open-webui at port 8080" , "blue")
        util.run_cloudflare(8080, "Open-webui Access:", path=os.path.join(os.getcwd(), "access", "cloudflare_open-webui_url.txt"))
        util.tost("Access STT engine at port 3401" , "blue")
        util.run_cloudflare(3401, "STT Access:", path=os.path.join(os.getcwd(), "access", "cloudflare_stt_url.txt"))
        # Create threads for both servers
        tts_thread = threading.Thread(
            target=run_tts,
            args=(tts_app, 3400),
            daemon=True
        )
        main_thread = threading.Thread(
            target=open_web_ui_plus,
            args=(open_webui_plus_app, 7800),
            daemon=True
        )

        # Start both servers
        tts_thread.start()
        main_thread.start()
        main_logger.info("Started both TTS and Main servers")

        # Keep the main thread alive
        while True:
            tts_thread.join(1)
            main_thread.join(1)
            
    except KeyboardInterrupt:
        main_logger.info("Shutting down servers...")
        print("\nShutting down servers...")
    except Exception as e:
        main_logger.error(f"Error occurred: {str(e)}")
        raise
import os
import sqlite3
import logging
import asyncio
import json
import secrets
import uuid
from datetime import datetime, timedelta
from threading import Thread
import subprocess
import util
# Third-party imports
from flask import Flask, request, jsonify, send_file, abort , render_template
from flask_cors import CORS
import edge_tts
from langdetect import detect


class Config:
    """Application configuration and initialization."""

    # Core settings
    DATABASE_PATH = os.path.join(os.getcwd() , "database" , "audio_files.db")
    AUDIO_DIR = os.path.join(os.getcwd() , "res")
    DATA_FOLDER = os.path.join(os.getcwd() , "data")
    util.make_dir(os.path.join(os.getcwd() , "database"))
    util.make_dir(AUDIO_DIR)
    util.make_dir(DATA_FOLDER)

    @classmethod
    def init_directories(cls):
        """Create necessary directories if they don't exist."""
        os.makedirs(cls.DATA_FOLDER, exist_ok=True)
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)

    @staticmethod
    def load_voice_mappings():
        """Load voice configuration from JSON file."""
        with open(os.path.join(os.getcwd() , "open-webui-plus" , "voices" , "voice_pack01.json"), 'r', encoding='utf-8') as f:
            return json.load(f)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Security Utilities
# ============================================================================

def generate_aes_key(key_length: int = 32) -> bytes:
    """
    Generate a secure AES key for encryption.

    Args:
        key_length (int): Length of the key (16, 24, or 32 bytes)
    Returns:
        bytes: Generated AES key
    """
    if key_length not in [16, 24, 32]:
        raise ValueError("key_length must be 16, 24, or 32 bytes")
    return secrets.token_bytes(key_length)

# ============================================================================
# Database Management
# ============================================================================

class DatabaseManager:
    """Handle database operations for audio files."""

    @staticmethod
    def init_db():
        """Initialize database with required tables."""
        with sqlite3.connect(Config.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    delete_at TIMESTAMP
                )
            ''')
            conn.commit()

    @staticmethod
    def add_file(file_id: str, filename: str, delete_at: datetime):
        """Add a new file record to the database."""
        with sqlite3.connect(Config.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO files (id, filename, delete_at) VALUES (?, ?, ?)',
                (file_id, filename, delete_at)
            )
            conn.commit()

# ============================================================================
# Voice Service
# ============================================================================

class VoiceService:
    """Handle voice-related operations and validations."""

    def __init__(self, voice_mappings):
        self.voice_mappings = voice_mappings

    def get_available_voices(self, language: str, gender: str = None) -> list:
        """
        Get available voices for a specific language and gender.

        Args:
            language (str): Language code
            gender (str, optional): 'Male' or 'Female'
        Returns:
            list: Available voice names
        """
        available_voices = [
            voice for voice, data in self.voice_mappings.items()
            if data['language'].startswith(language)
        ]

        if gender:
            available_voices = [
                voice for voice in available_voices
                if self.voice_mappings[voice]['gender'] == gender
            ]

        return available_voices

    def validate_voice(self, voice: str) -> bool:
        """Check if a voice is valid."""
        return voice in self.voice_mappings

    def get_voice_for_text(self, text: str, requested_voice: str) -> str:
        """
        Determine the most appropriate voice for the given text.

        Args:
            text (str): Input text
            requested_voice (str): Initially requested voice
        Returns:
            str: Selected voice name
        """
        detected_language = detect(text)
        voice_data = self.voice_mappings[requested_voice]

        if detected_language.startswith(voice_data['language']):
            return requested_voice

        # Try to find a voice with same gender and language
        available_voices = self.get_available_voices(
            detected_language,
            voice_data['gender']
        )
        if available_voices:
            return available_voices[0]

        # Try any voice with the correct language
        available_voices = self.get_available_voices(detected_language)
        if available_voices:
            return available_voices[0]

        raise ValueError("No suitable voice found for the detected language")

# ============================================================================
# File Cleanup Service
# ============================================================================

class CleanupService:
    """Handle periodic cleanup of old audio files."""

    @staticmethod
    async def delete_expired_files():
        """Delete files that have passed their expiration time."""
        while True:
            now = datetime.now()
            with sqlite3.connect(Config.DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT filename FROM files WHERE delete_at <= ?', (now,))

                for (filename,) in cursor.fetchall():
                    try:
                        os.remove(os.path.join(Config.AUDIO_DIR, filename))
                        cursor.execute('DELETE FROM files WHERE filename = ?', (filename,))
                    except FileNotFoundError:
                        logger.warning(f"File not found for deletion: {filename}")

                conn.commit()

            await asyncio.sleep(60)

    @classmethod
    def start(cls):
        """Start the cleanup service in a background thread."""
        thread = Thread(target=lambda: asyncio.run(cls.delete_expired_files()))
        thread.daemon = True
        thread.start()
def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = generate_aes_key()
    app.config['CORS_HEADERS'] = 'Content-Type'

    # Initialize CORS
    CORS(app)

    # Initialize services
    Config.init_directories()
    voice_service = VoiceService(Config.load_voice_mappings())
    

    @app.route('/v1/audio/speech', methods=['POST'])
    async def convert_text_to_speech():
        """Convert text to speech using Edge TTS."""
        data = request.get_json()
        text = data.get('input', '').replace("*", "")
        voice = data.get("model")
        speed = data.get('voice')

        # Validate input
        if not text:
            return jsonify(error="No text provided"), 400
        if not voice:
            return jsonify(error="No voice provided"), 400
        if not voice_service.validate_voice(voice):
            return jsonify(error="Invalid voice provided"), 400

        try:
            # Get appropriate voice
            voice = voice_service.get_voice_for_text(text, voice)

            # Generate unique filename
            unique_id = str(uuid.uuid4())
            output_file = f'{unique_id}.wav'
            output_path = os.path.join(Config.AUDIO_DIR, output_file)

            # Configure speech settings
            valid_speeds = {
                "normal": None,
                "slow": "-8%",
                "fast": "+12%"
            }

            rate = valid_speeds.get(speed)
            if speed not in valid_speeds:
                abort(404, description="Invalid rate. Use 'normal', 'slow', or 'fast'")

            # Generate speech
            communicate = edge_tts.Communicate(
                text,
                voice=voice,
                rate=rate if rate is not None else None
            )
            await communicate.save(output_path)

            # Record file for cleanup
            delete_at = datetime.now() + timedelta(minutes=3)
            DatabaseManager.add_file(unique_id, output_file, delete_at)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            abort(500, description=f"Error processing request: {str(e)}")

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'message': error.description}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'message': error.description}), 500
    @app.route('/v1/models', methods=['GET'])
    def get_available_voices():
        """Return list of all available voices and their details"""
        try:
            voices = Config.load_voice_mappings()
            # Group voices by language with better structure
            languages = {}
            for voice_id, details in voices.items():
                lang_code = details['language']
                if lang_code not in languages:
                    languages[lang_code] = {
                        'male': [],
                        'female': []
                    }

                # Create more detailed voice info
                voice_info = {
                    'id': voice_id,
                    'name': voice_id.split('Neural')[0],  # Remove Neural suffix
                    'display_name': voice_id.split('-')[-1].replace('Neural', ''),  # Get friendly name
                    'gender': details['gender'],
                    'language': details['language']
                }

                # Add to appropriate gender list
                if details['gender'].lower() == 'male':
                    languages[lang_code]['male'].append(voice_info)
                else:
                    languages[lang_code]['female'].append(voice_info)

            # Sort voices within each gender by name
            for lang in languages.values():
                lang['male'].sort(key=lambda x: x['name'])
                lang['female'].sort(key=lambda x: x['name'])

            # Return either JSON or HTML based on Accept header
            if 'text/html' in request.headers.get('Accept', ''):
                return render_template('voices.html', languages=languages)
            return jsonify(languages)

        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            abort(500, description="Error retrieving voice list")


    return app




from flask import Flask, request, jsonify
import os
from faster_whisper import WhisperModel
import tempfile
import torch
import time

app = Flask(__name__)

# T4-compatible model configurations
MODELS = {
    "base": {
        "size": "base",
        "description": "Whisper Base Model - Fast"
    },
    "small": {
        "size": "small",
        "description": "Whisper Small Model - Balanced"
    },
    "medium": {
        "size": "medium",
        "description": "Whisper Medium Model - Accurate"
    },
    "large-v3": {
        "size": "large-v3",
        "description": "Whisper Large V3 - Most Accurate"
    }
}

# Model cache to avoid reloading
loaded_models = {}

def get_model(model_id="whisper-1"):
    """Get or load the requested model"""
    model_size = MODELS.get(model_id, MODELS["whisper-1"])["size"]

    if model_size not in loaded_models:
        # Initialize Whisper model with GPU support
        loaded_models[model_size] = WhisperModel(
            model_size_or_path=model_size,
            device="cuda" if torch.cuda.is_available() else "cpu",
            compute_type="float16" if torch.cuda.is_available() else "float32",
            download_root="./models",
            cpu_threads=4,
            num_workers=1,
        )

    return loaded_models[model_size]

def transcribe_audio(audio_path, model_id="whisper-1", prompt=None, language=None):
    """
    Transcribe audio using selected whisper model
    """
    model = get_model(model_id)

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=400
        ),
        initial_prompt=prompt,
        language=language,
        temperature=0.0,
        condition_on_previous_text=False,
        no_speech_threshold=0.6
    )

    # Combine all segments
    full_text = " ".join(segment.text for segment in segments)

    # Match OpenAI Whisper API format
    return {
        "text": full_text,
        "task": "transcribe",
        "language": info.language,
        "duration": sum(segment.end - segment.start for segment in segments),
        "segments": [
            {
                "id": i,
                "seek": segment.start * 1000,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "tokens": [],
                "temperature": 0.0,
                "avg_logprob": -1.0,
                "compression_ratio": 1.0,
                "no_speech_prob": 0.0 if not hasattr(segment, 'no_speech_prob') else segment.no_speech_prob
            }
            for i, segment in enumerate(segments)
        ]
    }

@app.route('/whisper/v1/audio/transcriptions', methods=['POST'])
def handle_transcription():
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": {
                    "message": "No audio file provided",
                    "type": "invalid_request_error",
                    "code": "no_file"
                }
            }), 400

        file = request.files['file']
        model = request.form.get('model', 'whisper-1')
        prompt = request.form.get('prompt', None)
        language = request.form.get('language', None)

        if model not in MODELS:
            return jsonify({
                "error": {
                    "message": f"Model {model} not found",
                    "type": "invalid_request_error",
                    "code": "model_not_found"
                }
            }), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            result = transcribe_audio(temp_path, model, prompt, language)
            return jsonify(result), 200
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": "internal_error"
            }
        }), 500

@app.route('/whisper/v1/models', methods=['GET'])
def list_models():
    """
    OpenAI-compatible models endpoint with all available models
    """
    current_time = int(time.time())
    return jsonify({
        "data": [
            {
                "id": model_id,
                "object": "model",
                "created": current_time,
                "owned_by": "local",
                "permission": [],
                "root": model_id,
                "parent": None,
                "description": info["description"]
            }
            for model_id, info in MODELS.items()
        ]
    })

@app.route('/whisper/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "operational",
        "message": "Whisper API is healthy",
        "available_models": list(MODELS.keys())
    })
app.run(host='0.0.0.0', port=3401)

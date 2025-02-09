# Open-WebUI-Plus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/downloads/)

The upgraded version of [OpenWebUI](https://github.com/open-webui) with integrated STT engine and TTS support.

## 🌟 Overview

Welcome to **Open-WebUI-Plus** – an enhanced version of OpenWebUI that comes with built-in **TTS (Text-to-Speech)** and **STT (Speech-to-Text)** capabilities. This project provides a seamless, user-friendly interface for both voice and text interactions, designed for optimal performance across Windows, macOS, and Linux platforms.

## ✨ Features

- **Enhanced User Interface:** Modern, intuitive UI built on the original OpenWebUI foundation
- **Voice Integration:** 
  - Built-in Text-to-Speech (TTS) for natural voice output
  - Speech-to-Text (STT) capabilities for voice command recognition
- **Cross-Platform Support:** 
  - Compatible with Windows, macOS, and Linux
  - Requires Python 3.x
- **Simplified Setup:** One-command dependency installation
- **Flexible Configuration:** Easy customization of server settings, TTS/STT parameters

## 📥 Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/easy-ware/Open-WebUI-Plus.git
   cd Open-WebUI-Plus
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements/req.txt
   ```
   > Note: Use `pip3` if your system defaults to Python 2

## 🚀 Quick Start

1. **Launch the Server:**
   ```bash
   python open-webui-plus/server.py
   ```
   Alternative commands if needed:
   ```bash
   python3 open-webui-plus/server.py
   # OR
   python driver open-webui-plus/server.py
   ```

2. **Access the Interface:**
   Open your web browser and navigate to:
   ```
   http://localhost:7800
   ```

## ⚙️ Configuration

Customize your experience by modifying the settings in Open-webui Admin Settings console:

# TTS Settings
## Voice selection
### In the admin panel:
1. Go to the audio settings and select the TTS Settings.
2. In server select openai then in url set as `http://127.0.0.1:3400/v1`.
3. In TTS Voice select from
- `fast`
-  `slow`
-  `normal`
4. In TTS Model choose from availabel model ids get from `http://127.0.0.1:3400/v1/models` and copy the model id from there..
   


### STT Settings
- Language preferences
- Recognition accuracy
- Input device selection

### Server Configuration
- Port number (default: 5000)
- Log level
- API endpoints

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Original OpenWebUI developers
- Easy-Ware community
- All open-source contributors

## 📫 Support

- For bugs and features, please use the [Issue Tracker](https://github.com/easy-ware/Open-WebUI-Plus/issues)

---

Made with ❤️ by the Easy-Ware Team

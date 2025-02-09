### Open-WebUI-Plus
## The upgraded version for open-webui with stt engine and tts support...


---

```markdown
# Open-WebUI-Plus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/downloads/)

Welcome to **Open-WebUI-Plus** – an upgraded version of [OpenWebUI](https://github.com/search?q=OpenWebUI) that now comes packed with integrated **TTS (Text-to-Speech)** and **STT (Speech-to-Text)** support. This project provides an all-in-one, user-friendly interface for both voice and text interactions, built for flexibility and ease-of-use on Windows, macOS, and Linux.

---

## ✨ Features

- **Enhanced User Interface:** A modernized, intuitive UI built on top of the original OpenWebUI.
- **Integrated TTS & STT:** Enjoy built-in voice synthesis and speech recognition capabilities.
- **Cross-Platform Compatibility:** Runs smoothly on Windows, macOS, and Linux with Python 3.
- **Easy Setup:** Install all dependencies with a single command.
- **Customizable Configurations:** Easily modify server settings, TTS parameters, STT options, and more.

---

## 📥 Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/easy-ware/Open-WebUI-Plus.git
   cd Open-WebUI-Plus
   ```

2. **Install Dependencies:**

   Install the required Python packages using pip:

   ```bash
   pip install -r requirements/req.txt
   ```

   > **Note:** If your system defaults to Python 2, use `python3` instead.

---

## 🚀 Usage

Start the Open-WebUI-Plus server with one of the commands below:

- **Using the default Python command:**

   ```bash
   python open-webui-plus/server.py
   ```

- **Using Python 3 explicitly (if needed):**

   ```bash
   python3 open-webui-plus/server.py
   ```

- **Alternative Command (if using a driver script):**

   ```bash
   python driver open-webui-plus/server.py
   ```

Once the server is running, open your web browser and navigate to:

[http://localhost:5000](http://localhost:5000)

> **Tip:** If port `5000` is in use, adjust the port number in your configuration settings.

---

## ⚙️ Configuration

Customize your Open-WebUI-Plus experience by editing the configuration files (typically located in the `config/` directory, if provided). You can modify settings for:

- **TTS Options:** Select voices, adjust speed, pitch, etc.
- **STT Options:** Set language preferences and recognition parameters.
- **Server Settings:** Change port numbers, logging levels, and other parameters.

---

## 🤝 Contributing

Contributions are always welcome! To contribute:

1. **Fork the Repository.**
2. **Create a New Branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m "Add your feature or bugfix description"
   ```

4. **Push to Your Branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub with a detailed description of your changes.

For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- **Original OpenWebUI:** The inspiration behind Open-WebUI-Plus.
- **Easy-Ware Community:** For continuous feedback, testing, and support.
- **Open Source Contributors:** Thanks to the developers of the libraries and tools that made this project possible.

---

*Happy coding! Enjoy using Open-WebUI-Plus and feel free to [open an issue](https://github.com/easy-ware/Open-WebUI-Plus/issues) if you have any questions, suggestions, or need help.*

```

---

Feel free to modify any sections to better suit your project's evolving needs. Enjoy coding and sharing your enhanced web UI with the community!

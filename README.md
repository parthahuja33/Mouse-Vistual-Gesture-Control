# Mouse Visual Gesture Control

A production-ready virtual mouse application for hands-free computer control using camera-based hand gesture recognition.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](virtual_mouse/LICENSE)

---

## 🚀 Quick Start

```bash
cd virtual_mouse
pip install -r requirements.txt
python -m src.main --show-debug
```

---

## ✨ Features

- 🤚 Real-time hand gesture recognition (MediaPipe)
- 🖱️ Full mouse control: move, click, drag, scroll
- ⚡ Performance optimized: 15-25% CPU usage
- 🎯 High accuracy with gesture smoothing
- 🪟 Cross-platform: Windows, Linux, macOS
- 🎛️ Fully configurable via environment variables

---

## 🎮 Gesture Controls

| Gesture | Action |
|---------|--------|
| **✋ Index Finger** | Move Cursor |
| **👌 Pinch** | Click |
| **🤏 Hold Pinch** | Drag |
| **✌️ Middle Finger Up/Down** | Scroll |

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- Webcam
- Windows 10/11, Linux, or macOS

### Install & Run

```bash
cd virtual_mouse

# Option 1: Python command
pip install -r requirements.txt
python -m src.main --show-debug

# Option 2: Launcher script
./run_virtual_mouse.sh  # Linux/macOS
run_virtual_mouse.bat   # Windows
```

---

## ⚙️ Configuration

### Command Line

```bash
python -m src.main --auto-start --show-debug --log-level DEBUG
```

### Environment Variables

```bash
# Camera
VM_CAMERA_RESOLUTION=960x540
VM_CAMERA_FPS=30

# Gestures
VM_GESTURE_SMOOTHING=0.25
VM_GESTURE_CLICK_THRESHOLD=0.035

# App
VM_APP_SHOW_DEBUG=false
VM_LOG_LEVEL=INFO
```

**Full configuration**: See `virtual_mouse/env.example`

---

## 🏗️ Project Structure

```
virtual_mouse/
├── src/
│   ├── main.py                   # Entry point
│   └── virtual_mouse/
│       ├── camera_module.py      # Camera capture
│       ├── hand_tracking.py      # MediaPipe wrapper
│       ├── gesture_controller.py # Gesture logic
│       └── virtual_mouse.py      # Core engine
│
├── utils/
│   ├── config.py                 # Configuration
│   └── logger.py                 # Logging
│
├── tests/                        # Unit tests
└── README.md                     # Full documentation
```

---

## 📊 Performance

| Mode | CPU | Memory | FPS |
|------|-----|--------|-----|
| Active | 15-25% | ~100MB | 30 |
| Idle | 3-8% | ~60MB | 10 |

---

## 🐛 Troubleshooting

**Camera not opening?**
- Close other apps using camera
- Try: `VM_CAMERA_INDEX=1`

**Hand not detected?**
- Ensure good lighting
- Position hand 1-2 feet away

**Jittery cursor?**
- Increase smoothing: `VM_GESTURE_SMOOTHING=0.1`

**More help**: See `virtual_mouse/README.md`

---

## 🧪 Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
pip install pytest black mypy pylint

# Test
pytest tests/ -v

# Format
black src/ utils/ tests/
```

---

## 📄 License

MIT License - see [LICENSE](virtual_mouse/LICENSE)

---

## 🙏 Acknowledgments

- MediaPipe - Hand tracking
- OpenCV - Computer vision
- PyAutoGUI - Mouse control

---

**⭐ Star this repo • 🐛 Report issues • 🤝 Contribute**

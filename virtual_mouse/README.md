# 🖱️ Virtual Mouse - Camera Gesture Control

A lightweight, production-ready virtual mouse application that enables hands-free computer control using camera-based hand gesture recognition.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Features

- 🤚 **Real-time Hand Tracking** - MediaPipe-powered 21-point landmark detection
- 🖱️ **Full Mouse Control** - Move, click, drag, and scroll
- ⚡ **Performance Optimized** - 15-25% CPU usage with dynamic idle mode
- 🎯 **High Accuracy** - Advanced smoothing and gesture filtering
- 🪟 **Cross-Platform** - Windows, Linux, and macOS support
- 🎛️ **Fully Configurable** - Environment variables for all parameters

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Webcam (USB or built-in)
- Windows 10/11, Linux, or macOS

### Installation

```bash
# Navigate to the project
cd virtual_mouse

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main --show-debug
```

### Using Launcher Scripts

**Windows**:
```cmd
run_virtual_mouse.bat
```

**Linux/macOS**:
```bash
./run_virtual_mouse.sh
```

---

## 🎮 Gesture Controls

| Gesture | Action | How to Perform |
|---------|--------|----------------|
| **✋ Move Cursor** | Control pointer | Extend index finger, move hand |
| **👌 Click** | Single click | Pinch thumb and index fingertips together |
| **🤏 Drag** | Click and drag | Pinch and hold while moving |
| **✌️ Scroll** | Vertical scroll | Move middle finger up/down relative to index |

---

## ⚙️ Configuration

### Command Line Options

```bash
# Start immediately with debug visualization
python -m src.main --auto-start --show-debug

# Custom log level
python -m src.main --log-level DEBUG
```

### Environment Variables

Create a `.env` file or set system environment variables:

#### Camera Settings
```bash
VM_CAMERA_INDEX=0                      # Camera device index (0 = default)
VM_CAMERA_RESOLUTION=960x540           # Active resolution
VM_CAMERA_FPS=30                       # Target frames per second
VM_CAMERA_IDLE_RESOLUTION=640x360      # Idle mode resolution
VM_CAMERA_MIRROR=true                  # Mirror camera horizontally
```

#### Gesture Tuning
```bash
VM_GESTURE_SMOOTHING=0.25              # Pointer smoothing (0.0-1.0)
VM_GESTURE_CLICK_THRESHOLD=0.035       # Pinch distance for click
VM_GESTURE_SCROLL_THRESHOLD=0.12       # Vertical finger delta for scroll
VM_GESTURE_DEBOUNCE_MS=180             # Click debounce milliseconds
```

#### Application Settings
```bash
VM_APP_SHOW_DEBUG=false                # Show debug window
VM_APP_AUTO_START=false                # Auto-start on launch
VM_APP_MAX_INACTIVE_SECONDS=10.0       # Idle timeout
VM_LOG_LEVEL=INFO                      # Logging level
```

**Full configuration**: See `env.example`

---

## 🏗️ Architecture

### Project Structure

```
virtual_mouse/
├── src/
│   ├── main.py                     # CLI entry point
│   └── virtual_mouse/
│       ├── camera_module.py        # Camera capture
│       ├── hand_tracking.py        # MediaPipe hand detection
│       ├── gesture_controller.py   # Gesture interpretation
│       └── virtual_mouse.py        # Core application engine
│
├── utils/
│   ├── config.py                   # Configuration management
│   └── logger.py                   # Logging infrastructure
│
├── tests/
│   └── test_gestures.py            # Unit tests
│
├── requirements.txt                # Python dependencies
├── setup.py                        # Package installation
├── README.md                       # This file
└── LICENSE                         # MIT License
```

### How It Works

```
Camera Frame → Hand Tracker → Gesture Controller → Pointer Control → OS Mouse
     ↓              ↓                 ↓                   ↓
  OpenCV       MediaPipe      Custom Logic         PyAutoGUI
```

**Processing Pipeline**:
1. **Camera**: Captures frames in background thread
2. **Hand Tracker**: Detects 21 hand landmarks using MediaPipe
3. **Gesture Controller**: Interprets landmarks into gestures
4. **Pointer Controller**: Executes mouse actions via PyAutoGUI

---

## ⚡ Performance

### CPU & Memory Usage

| Scenario | CPU Usage | Memory | FPS |
|----------|-----------|--------|-----|
| Active Tracking | 15-25% | ~100MB | 30 |
| Idle Mode | 3-8% | ~60MB | 10 |

*Tested on: Intel i5-10th Gen, 8GB RAM, Windows 11*

### Optimization Features

- **Dynamic Resolution**: 960x540 active → 640x360 idle
- **Frame Skipping**: Reduces processing when no hand detected
- **Threaded Camera**: Non-blocking frame capture
- **Gesture Smoothing**: Exponential moving average filter

### Performance Tips

**For Low-End Systems**:
```bash
VM_CAMERA_RESOLUTION=640x360
VM_CAMERA_FPS=15
VM_GESTURE_SMOOTHING=0.3
```

**For High Accuracy**:
```bash
VM_CAMERA_RESOLUTION=1280x720
VM_GESTURE_SMOOTHING=0.15
```

---

## 🐛 Troubleshooting

### Camera Not Opening

**Symptoms**: `RuntimeError: Unable to open camera index 0`

**Solutions**:
- Close other apps using camera (Zoom, Skype, etc.)
- Try different camera: `VM_CAMERA_INDEX=1`
- Check camera permissions in system settings

### Hand Not Detected

**Symptoms**: No landmarks visible in debug window

**Solutions**:
- Ensure good lighting (front-facing light recommended)
- Position hand 1-2 feet from camera
- Show full hand with fingers visible
- Clean camera lens

### Jittery Cursor

**Symptoms**: Cursor shakes during movement

**Solutions**:
- Increase smoothing: `VM_GESTURE_SMOOTHING=0.1`
- Reduce FPS: `VM_CAMERA_FPS=20`
- Stabilize hand (rest elbow on desk)

### Clicks Not Registering

**Symptoms**: Pinching doesn't trigger clicks

**Solutions**:
- Increase threshold: `VM_GESTURE_CLICK_THRESHOLD=0.05`
- Reduce debounce: `VM_GESTURE_DEBOUNCE_MS=100`
- Pinch more firmly (closer contact)

### High CPU Usage

**Symptoms**: Application consumes 40%+ CPU

**Solutions**:
- Reduce resolution: `VM_CAMERA_RESOLUTION=640x360`
- Lower FPS: `VM_CAMERA_FPS=15`
- Disable debug window
- Enable idle timeout: `VM_APP_MAX_INACTIVE_SECONDS=5.0`

---

## 🧪 Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest black mypy pylint
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html tests/
```

### Code Quality

```bash
# Format code
black src/ utils/ tests/

# Type checking
mypy src/ utils/

# Linting
pylint src/ utils/
```

---

## 📦 Dependencies

### Production
- **opencv-python** (4.10.0+) - Camera capture and image processing
- **mediapipe** (0.10.14+) - Hand landmark detection
- **pyautogui** (0.9.54+) - Cross-platform mouse control
- **numpy** (1.26.0+) - Numerical operations

### Development
- **pytest** (7.4.0+) - Unit testing
- **black** - Code formatting
- **mypy** - Type checking
- **pylint** - Code linting

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `pytest tests/`
5. Format code: `black src/ utils/ tests/`
6. Commit: `git commit -m "Add amazing feature"`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Copyright (c) 2025 Virtual Mouse Contributors

Permission is hereby granted, free of charge, to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, subject to the conditions in the LICENSE file.
```

---

## 🙏 Acknowledgments

- **MediaPipe** - Google's hand tracking solution
- **OpenCV** - Computer vision foundation
- **PyAutoGUI** - Cross-platform mouse control
- **Python Community** - Excellent libraries and tools

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Mouse-Visual-Gesture-Control/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Mouse-Visual-Gesture-Control/discussions)

---

**⭐ Star this repo if you find it useful!**  
**🐛 Report bugs to help us improve!**  
**🤝 Contribute to make it even better!**

---

*Made with ❤️ for hands-free computing*

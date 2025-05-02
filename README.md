# ThermalImageMosaic v1.0
The Thermal Image Mosaic is a cross-platform graphical application that allows users to visually compare, align, and combine thermal and RGB images on a unified working canvas.

The tool supports drag-and-drop image placement, per-image transparency and color channel adjustments, and high-resolution image export. It is designed for use in research, inspections, or any scenario where visual fusion of infrared and visible spectrum images is needed.
![canvas_snapshot_20250502_085721](https://github.com/user-attachments/assets/bfb8f644-2c3d-4c55-9804-930ee68eec53)

---

## Features

- 🖱️ Drag & drop support for thermal and RGB images
- 🖼️ Miniature image previews with numbering
- 🎛️ Per-image alpha and RGB channel adjustments (via right-click)
- 🔲 Visual alignment and manual repositioning
- 📁 Export merged thermal and RGB mosaics
- 🧾 Help menu with documentation
- ⌨️ Delete key support and red selection box(macOS)
- 📌 Windows `.ico` support for a custom application icon

---

## System Requirements
	
	Python version: 3.10 recommended (tested with 3.10.x)
	Python can be downloaded from: https://python.org
	Supported operating systems:
	•	Windows 10 / 11
	•	Linux (e.g., Ubuntu 22.04, Linux Mint)
	•	macOS 11 “Big Sur” or later

---

## Folder Structure
	├── ThermalImageMosaic.py
	├── main_window.py
	├── constants.py
	├── image_loader.py
	├── save_images.py
	├── images/
	│   ├── rgb/
	│   └── termal/
	├── help_documentation.pdf
	└── icon.png

---

## Installation

	To run the program, install the following external Python libraries:
	•	pip install pillow
	•	pip install tkinterdnd2
		
		For Linux systems, you may also need to install additional packages:
	•	sudo apt install python3-tk python3-dev

---

## Running the Application
	Use the terminal or command prompt:
	
	python ThermalImageMosaic.py

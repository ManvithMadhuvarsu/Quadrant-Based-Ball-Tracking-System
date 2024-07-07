# Quadrant-Based-Ball-Tracking-System
This Python application tracks colored balls within specified quadrants in videos. It allows users to define quadrants interactively, logs entry and exit events of each ball, and generates processed video outputs.

# Features
Interactive Quadrant Definition: Define up to 4 quadrants per video frame for ball tracking.
Real-Time Tracking: Detects and tracks colored balls (orange, white, greenish-blue, yellow) across frames.
Event Logging: Records entry and exit events of each ball within defined quadrants.
Output Generation: Saves processed video with overlaid tracking and logs events to a text file.

# Requirements
Python 3.x
OpenCV (pip install opencv-python)
Tkinter (usually included with Python installations)

# Usage
Select Input Video: Choose an MP4 video file containing the balls to track.
Define Quadrants: Click to define each quadrant on the video frame.
Process Video: Generate a processed video with tracked balls and save event logs.

# Installation
Clone the repository:
```
git clone https://github.com/ManvithMadhuvarsu/Quadrant-Based-Ball-Tracking-System.git
```
# Install dependencies:
```
pip install opencv-python
```

# Run the application:
```
python ball_tracking_app.py
```

# Contributing
Contributions are welcome! Please fork the repository and submit pull requests.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

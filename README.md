# Build an XRP Line-Following Robot Using a HuskyLens AI Vision Camera
A self-guided robotics, computer vision, and control-systems project for high-school students.

## Introduction
Build a line-following robot using an XRP robot and a DFRobot HuskyLens (SEN0305) AI vision sensor. The HuskyLens provides visual data, and the XRP board (with the RP2350 microcontroller) reads this data and drives the motors using PID controllers for stable line tracking.

**Learning Objectives:**
- How to read sensor data from the HuskyLens over I²C
- How differential-drive robots steer
- How PID control stabilizes robot motion
- How to tune a real controller through experimentation

**You’ll end with a robot that:**
- Detects and tracks a line using computer vision
- Computes steering corrections using PID control
- Adjusts motor speeds to follow the path accurately
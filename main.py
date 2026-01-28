from XRPLib.defaults import drivetrain
from XRPLib.pid import PID
from lib.i2c import HuskyLensLibrary
from machine import Pin
import time

# Initialize HuskyLens camera
huskylens = HuskyLensLibrary(scl=Pin(5), sda=Pin(4), channel=0, address=0x32)
huskylens.algorthim("ALGORITHM_LINE_TRACKING")

# Target positions
TARGET_X = 160  # Center of camera (320/2 pixels)
TARGET_HEAD_Y = 20  # Top of camera
TARGET_TAIL_Y = 240  # Bottom of camera

# Initialize PID controllers
# - kp: proportional gain (main response to error)
# - ki: integral gain (eliminates steady-state error, typically 10-100x smaller than kp)
# - kd: derivative gain (reduces overshoot/oscillations, typically 10-100x smaller than kp)
# - max_integral: prevents integral windup (accumulation of large errors)
x_controller = PID(
    kp=0.01,           
    ki=0.001,          
    kd=0.002,          
    min_output=-0.3,
    max_output=0.3,
    max_integral=50,   
    tolerance=10
)
y_controller = PID(
    kp=0.03,           
    ki=0.001,          
    kd=0.002,          
    min_output=-0.3,
    max_output=0.3,
    max_integral=50,   
    tolerance=25
)

while True:
    arrows = husky.arrows()
    
    if arrows and len(arrows) > 0:
        # Use the first arrow detected
        arrow = arrows[0]

        arrow_center_x = (arrow.xHead + arrow.xTail) / 2

        # Positive error means arrow is to the left, robot should turn right
        # Negative error means arrow is to the right, robot should turn left
        x_error = TARGET_X - arrow_center_x
        
        # Positive error means head is too low (yHead > 0), robot should move backward
        # Negative error means head is too high (yHead < 0), robot should move forward
        y_error = arrow.yHead - TARGET_HEAD_Y
        
        turn_output = x_controller.update(x_error) # tolerance checking internally
        straight_output = -y_controller.update(y_error)
        
        # Check if both controllers are within tolerance
        if x_controller.is_done() and y_controller.is_done():
            # Robot is positioned correctly, drive forward with effort 0.2
            drivetrain.arcade(0.2, 0)
        else:
            # Adjust robot's position based on the error
            drivetrain.arcade(straight_output, turn_output)
        
        # Output for fine tuning and debugging
        print(f"Arrow: head=({arrow.xHead},{arrow.yHead}), tail=({arrow.xTail},{arrow.yTail})")
        print(f"Errors: x={x_error:.1f}, y={y_error:.1f} | Outputs: turn={turn_output:.3f}, straight={straight_output:.3f}")
        print(f"Within tolerance: x={x_controller.is_done()}, y={y_controller.is_done()}")
    else:
        # No arrows detected, stop the robot and clear controller history
        drivetrain.stop()
        x_controller.clear_history()
        y_controller.clear_history()
    
    # Small delay for control loop
    time.sleep(0.05)

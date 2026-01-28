from .i2c import HuskyLensLibrary
from machine import Pin
import time

# Initialize HuskyLens camera
huskylens = HuskyLensLibrary(scl=Pin(5), sda=Pin(4), channel=0, address=0x32)
huskylens.algorthim("ALGORITHM_LINE_TRACKING")

while True:
    arrows = husky.arrows()
    
    if arrows and len(arrows) > 0:
        # Use the first arrow detected
        arrow = arrows[0]
        print(f"Arrow: head = ({arrow.xHead}, {arrow.yHead}), tail = ({arrow.xTail}, {arrow.yTail})")
        
    # Small delay for the loop
    time.sleep(0.05)

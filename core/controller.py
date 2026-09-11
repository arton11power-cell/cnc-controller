"""CNC Machine Controller Logic"""


class CNCController:
    """Main controller for CNC machine operations"""

    def __init__(self):
        """Initialize CNC controller"""
        self.is_running = False
        self.current_position = {'X': 0, 'Y': 0, 'Z': 0}
        self.feed_rate = 100
        self.spindle_speed = 0

    def start(self):
        """Start the machine"""
        self.is_running = True
        print("CNC Machine started")

    def stop(self):
        """Stop the machine"""
        self.is_running = False
        print("CNC Machine stopped")

    def move_axis(self, axis, distance):
        """Move specific axis"""
        if axis in self.current_position:
            self.current_position[axis] += distance
            print(f"Moved {axis} by {distance}")

    def set_feed_rate(self, rate):
        """Set feed rate"""
        self.feed_rate = rate
        print(f"Feed rate set to {rate}")

    def set_spindle_speed(self, speed):
        """Set spindle speed"""
        self.spindle_speed = speed
        print(f"Spindle speed set to {speed}")

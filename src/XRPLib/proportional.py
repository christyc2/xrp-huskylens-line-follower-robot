from .controller import Controller

"""
Proportional (P-only) controller
"""

class Proportional(Controller):

    def __init__(self,
                 kp = 1.0,
                 min_output = 0.0,
                 max_output = 1.0,
                 tolerance = 0.1
                 ):
        """
        :param kp: proportional gain
        :param min_output: minimum output
        :param max_output: maximum output
        :param tolerance: tolerance for exit condition
        """
        self.kp = kp
        self.min_output = min_output
        self.max_output = max_output
        self.tolerance = tolerance
        
        # Store current error for is_done() check
        self.current_error = 0

    def update(self, error: float, debug: bool = False) -> float:
        """
        Handle a new update of this proportional controller given an error.

        :param error: The error of the system being controlled by this controller
        :type error: float

        :return: The system output from the controller, to be used as an effort value or for any other purpose
        :rtype: float
        """
        self.current_error = error
        
        # Calculate proportional output
        output = self.kp * error
        
        # Bound output by minimum
        if output > 0:
            output = max(self.min_output, output)
        else:
            output = min(-self.min_output, output)
        
        # Bound output by maximum
        output = max(-self.max_output, min(self.max_output, output))

        if debug:
            print(f"Proportional output: {output}, error: {error}, kp: {self.kp}")

        return output
    
    def is_done(self) -> bool:
        """
        :return: if error is within tolerance
        :rtype: bool
        """
        return abs(self.current_error) < self.tolerance
    
    def clear_history(self):
        """
        Clears the current error state
        """
        self.current_error = 0

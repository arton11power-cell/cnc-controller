"""G-code parser for CNC Controller"""


class GCodeParser:
    """Parser for G-code commands"""

    def __init__(self):
        """Initialize G-code parser"""
        self.commands = []

    def parse(self, gcode_text):
        """Parse G-code text into commands"""
        lines = gcode_text.strip().split('\n')
        self.commands = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            self.commands.append(line)

        return self.commands

    def get_commands(self):
        """Get parsed commands"""
        return self.commands

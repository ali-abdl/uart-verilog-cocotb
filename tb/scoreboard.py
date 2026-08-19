"""Shared scoreboard for UART testbenches."""


class Scoreboard:
    """Tracks expected values and compares them against observed ones."""

    def __init__(self, log, name="scoreboard", max_reports=10):
        self.log = log
        self.name = name
        self.expected = []
        self.checked = 0
        self.errors = 0
        self.max_reports = max_reports

    def expect(self, value):
        self.expected.append(value)

    def check(self, actual):
        if not self.expected:
            self.errors += 1
            self.log.error(f"[{self.name}] got 0x{actual:02X} with nothing expected")
            return

        exp = self.expected.pop(0)
        self.checked += 1
        if actual != exp:
            self.errors += 1
            if self.errors <= self.max_reports:
                self.log.error(
                    f"[{self.name}] mismatch: expected 0x{exp:02X}, got 0x{actual:02X}"
                )
            elif self.errors == self.max_reports + 1:
                self.log.error(f"[{self.name}] ... suppressing further reports")

    def report(self):
        self.log.info(f"[{self.name}] {self.checked} bytes checked, {self.errors} errors")
"""Acceptance checks shared by simulation and regression tests."""
import re


def check_simulation(text, returncode):
    summaries = re.findall(r"FINAL RESULTS:\s*(\d+) PASSED,\s*(\d+) FAILED", text)
    if (returncode or summaries != [("36", "0")]
            or re.search(r"\[FAIL\]|TIMEOUT|ERROR", text)):
        raise ValueError("Simulation did not complete all 36 comparisons cleanly")

import math
from datetime import datetime
import errno
import os
import sys

INT8_MIN,  INT8_MAX  = -128, 127
INT32_MIN, INT32_MAX = -2147483648, 2147483647

def _nint_away_from_zero(x: float) -> int:
    if x >= 0:
        return math.floor(x + 0.5)
    return math.ceil(x - 0.5)

def _round_half_away_from_zero(x: float) -> int:
    return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)

def roundc_int32(x: float) -> int:
    return _roundc_impl(x, INT32_MIN, INT32_MAX)

def roundc_int8(x: float) -> int:
    return _roundc_impl(x, INT8_MIN, INT8_MAX)

def _roundc_impl(x: float, min_value: int, max_value: int) -> int:
    if x > max_value:
        x_clipped = float(max_value)
    elif x < min_value:
        x_clipped = float(min_value)
    else:
        x_clipped = x

    if abs(x_clipped - math.floor(x_clipped) - 0.5) < sys.float_info.epsilon:
        if x_clipped > 0:
            if abs(math.trunc(x_clipped)) % 2 == 0:
                return math.floor(x_clipped)
            else:
                return math.ceil(x_clipped)
        else:
            if abs(math.trunc(x_clipped)) % 2 == 0:
                return math.ceil(x_clipped)
            else:
                return math.floor(x_clipped)

    return _nint_away_from_zero(x_clipped)

def roundc(x: float, mold=1) -> int:
    if mold == "int8":
        return roundc_int8(x)
    return roundc_int32(x)

def open_file(filename: str, mode: str):
    try:
        return open(filename.strip(), mode.strip(), encoding="utf-8")
    except OSError as e:
        return None


def GetVersionString():
    # Returns a string containing the version number (major+minor).
    return "7.3"

def GetReleaseDate():
    # Returns a string containing the month and year of the release.
    return 'January 2026'

def GetAquaCropDescriptionWithTimeStamp():
    # Same as GetAquaCropDescription(), but with a time stamp.

    now = datetime.now()
    datestr = now.strftime("%d-%m-%Y")
    timestr = now.strftime("%H:%M:%S")

    return (
        GetAquaCropDescription()
        + " - Output created on (date) : "
        + datestr
        + "   at (time) : "
        + timestr
    )

def GetAquaCropDescription():
    # Returns a string with the aquacrop version and release date.

    return "AquaCrop " + GetVersionString() + " (" + GetReleaseDate() + ")"

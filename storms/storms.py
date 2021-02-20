"""Create design storms for modelling in MIKE software.

Given IDF data, this package lets you create Chicago design storms. Load in the
IDF data. Interpret it to the IDF function. Create the Chicago design storm and
export it to .dfs0 format.

"""

from scipy.optimize import curve_fit


def idf(duration, A, B, C):
    """Calculate intensity for specified duration given IDF parameters A, B, and C.

    Args:
        duration: duration to calculate intensity for. Typically in minutes,
                  but depends on input data.
        A: constant A in equation i = A / (duration + B)**C.
        B: constant B in equation i = A / (duration + B)**C.
        C: constant C in equation i = A / (duration + B)**C.

    Returns:
        Returns the intensity. Typically in mm/hr, but depends on input data.

    """
    return A / (duration + B)**C


def getABC(durations, intensities):
    """Calculate IDF ABC parameters based on set of durations and intensities.

    Args:
        durations: an array of the durations, typically in minutes
        intensities: an array of the intensities, typically in mm/hr

    Returns:
        Returns A, B, C as a tuple.

    """

    popt, pcov = curve_fit(idf, durations, intensities)

    return (popt[0], popt[1], popt[2])

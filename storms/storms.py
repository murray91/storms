"""Create design storms for modelling in MIKE software.

Given IDF data, this package lets you create Chicago design storms. Load in the
IDF data. Interpret it to the IDF function. Create the Chicago design storm and
export it to .dfs0 format.

"""

from scipy.optimize import curve_fit
from scipy.integrate import quad
import numpy as np
import pandas as pd
from mikeio import Dfs0, Dataset
from mikeio.eum import ItemInfo, EUMType, EUMUnit
from datetime import datetime, timedelta
from DHI.Generic.MikeZero.DFS import DataValueType


def idf(duration, A, B, C):
    """Calculate intensity for specified duration given IDF parameters A, B, and C.

    Args:
        duration: duration to calculate intensity for. Unit: minutes
        A: constant A in equation i = A / (duration + B)**C.
        B: constant B in equation i = A / (duration + B)**C.
        C: constant C in equation i = A / (duration + B)**C.

    Returns:
        Returns intensity in mm/hr.

    """
    return A / (duration + B)**C


def getABC(durations, intensities):
    """Calculate IDF ABC parameters based on set of durations and intensities.

    Args:
        durations: an array of the durations. Unit: minutes
        intensities: an array of the intensities. Unit: mm/hr

    Returns:
        Returns A, B, C as a tuple.

    """

    popt, pcov = curve_fit(idf, durations, intensities)

    return (popt[0], popt[1], popt[2])

def getABC_lsq(durations, intensities):
    """Calculate IDF ABC parameters based on set of durations and intensities.
       Uses a different method than getABC.
       NOTE: IT IS NOT IMPLEMENTED, BUT CODE IS IN COMMENTS.

    Args:
        durations: an array of the durations. Unit: minutes
        intensities: an array of the intensities. Unit: mm/hr

    Returns:
        Returns A, B, C as a tuple.

    """

    #from sklearn.linear_model import LinearRegression
    #from scipy.optimize import minimize

    #def linear_reg(b, durations, intensities):
    #    X = np.log(durations+b).reshape((-1,1))
    #    Y = np.log(intensities)
    #    model = LinearRegression()
    #    model.fit(X,Y)
    #    return 1 - model.score(X,Y)

    #res = minimize(linear_reg, 5, (durations, intensities))
    #b = res.x[0]
    #X = np.log(durations+b).reshape((-1,1))
    #Y = np.log(intensities)
    #model = LinearRegression()
    #model.fit(X,Y)
    #a = np.exp(model.intercept_)
    #c = -model.coef_[0]

    return 1


def ib(tb, r, a, b, c):
    """Chicago design storm equation - intensity before peak.
        Helper for i function.

    Args:
        tb: time before peak in minutes (measured from peak towards beginning)
        r: time to peak ratio (peak time divided by total duration)
        a: IDF A parameter - can be calculated from getABC
        b: IDF B parameter - can be calculated from getABC
        c: IDF C parameter  - can be calculated from getABC

    Returns:
        Returns intensity in mm/hr.

    """
    return a*((1-c)*tb/r+b)/((tb/r)+b)**(c+1)


def ia(ta, r, a, b, c):
    """Chicago design storm equation - intensity after peak. Helper for i function.

    Args:
        ta: time after peak in minutes (measured from peak towards end)
        r: time to peak ratio (peak time divided by total duration)
        a: IDF A parameter - can be calculated from getABC
        b: IDF B parameter - can be calculated from getABC
        c: IDF C parameter  - can be calculated from getABC

    Returns:
        Returns intensity in mm/hr.

    """
    return a*((1-c)*ta/(1-r)+b)/((ta/(1-r))+b)**(c+1)


def i(t, T, r, a, b, c):
    """Chicago design storm equation - intensity. Uses ia and ib functions.

    Args:
        t: time in minutes from storm eginning
        T: total storm duration in minutes
        r: time to peak ratio (peak time divided by total duration)
        a: IDF A parameter - can be calculated from getABC
        b: IDF B parameter - can be calculated from getABC
        c: IDF C parameter  - can be calculated from getABC

    Returns:
        Returns intensity in mm/hr.

    """
    if t < T*r:
        return ib(T*r - t, r, a, b, c)
    elif t > T*r:
        return ia(t - T*r, r, a, b, c)
    else:
        # Should be infinity, but this does the job
        return 1000


def makeChicagoStorm(T, r, dt, a, b, c):
    """Makes a chicago design storm.

    Args:
        T: total storm duration in minutes
        r: time to peak ration (peak time divided by total duration)
        dt: time step in minutes
        a: IDF A parameter - can be calculated from getABC
        b: IDF B parameter - can be calculated from getABC
        c: IDF C parameter  - can be calculated from getABC

    Returns:
        Returns tuple of (dt, array of intensities).

    """

    # make time axis
    times = np.arange(0-dt*r, T-dt*r, dt)

    # determine time step averaged intensities
    values = [0]
    for time in times:
        values.append(quad(i, time, time+dt, args=(T, r, a, b, c))[0]/dt)

    return (dt, values)


def stormToDfs0(filename, stormname, dt, values,
                starttime=datetime(2021, 1, 1, 12)):
    """Outputs a storm to dfs0 format.

    Args:
        filename: absolute path to dfs0 to be created
        stormname: string of name to give to data in dfs0
        dt: time step in minutes
        values: array of storm intensities in mm/hr
        starttime: datetime object of when storm should start

    Returns:
        No return value, just creates dfs0.

    """

    nt = len(values)
    storm_data = np.array(values)

    # setup dfs0 dataset
    ds = Dataset(
        data=[storm_data],
        time=pd.date_range(start=starttime,
                           end=(starttime+timedelta(minutes=(nt-1)*dt)),
                           periods=nt),
        items=[ItemInfo(stormname, EUMType.Rainfall_Intensity,
                        EUMUnit.mm_per_hour)]
    )

    # write to dfs0
    dfs = Dfs0()
    dfs.write(filename,
              data=ds,
              title=stormname,
              data_value_type=[DataValueType.MeanStepBackward])

    return True

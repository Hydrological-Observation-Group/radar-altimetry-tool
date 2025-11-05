# author: luo xin, 
# creat: 2025-11-05
# des: Time formats conversions. year-month-day, day-of-year, decimal year, etc.

import numpy as np
from astropy.time import Time

def hz01_hz20(data_01hz, time_01hz, time_20hz, interp_method='nearest'):
    '''
    des: convert 01hz data to 20hz data through time nearest/linear interpolation.
    '''
    time_20hz_ = np.expand_dims(time_20hz, axis=1)
    dif_time = abs(time_20hz_ - time_01hz)
    ind_min = dif_time.argmin(axis=1)
    if interp_method == 'nearest':
        data_20hz = data_01hz[ind_min]
    elif interp_method == 'linear':
        data_20hz = np.interp(time_20hz, time_01hz, data_01hz)
    return data_20hz

def dt64_to_dyr(dt64, precision = 'D'):
    """
    des: convert datetime64 (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS) to decimal year format.    
    e.g., '2020-05-23T03:25:22.959373696' -> 2020.3907103825136.
    args:
        dt64: np.datetime64 format time
        precision: the precision of datetime64, 
                    e.g., 'D' for days, 's' for seconds, 
                            'ms' for milliseconds, 'us' for microseconds...
    """
    if isinstance(dt64, str):
        dt64 = np.datetime64(dt64)
    year = dt64.astype('M8[Y]')
    dyr_part = (dt64 - year).astype(f'timedelta64[{precision}]')
    year_next = year + np.timedelta64(1, 'Y')
    dyr_part_of_year = (year_next.astype(f'M8[{precision}]') - 
                        year.astype(f'M8[{precision}]')).astype(f'timedelta64[{precision}]')
    dt_float = 1970 + year.astype(float) + dyr_part / (dyr_part_of_year)
    return dt_float


### convert time (second format) to decimal year
def second_to_dyr(time_second, time_start='2000-01-01 00:00:00.0'):
    ''' 
    des: convert time (second format) to decimal year. This function suitable for the jason data, sentinel-3 data,
        and the cryosat2 data for time conversion.
    input: 
        time_second: seconds from the time start.
    return: 
        time_second_dyr: decimal date

    '''
    second_start = Time(time_start)         ## the start of the second time, some case should be 1970.1.1
    second_start_gps = Time(second_start, format="gps").value   ## seconds that elapse since gps time.
    time_start = time_second + second_start_gps     ## seconds between time_start and gps time + seconds between gps time and the given time_second.
    time_start_gps = Time(time_start, format="gps")
    time_second_dyr = Time(time_start_gps, format="decimalyear").value
    return time_second_dyr
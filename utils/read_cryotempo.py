# author: xin luo, 
# create: xin luo, 2023.1.17.
# des: read in and write out cryotempo data (such as eolis point).
## 1) the original .nc data will be convert to .h5 data.
## 2) the second time format will be convert to decimal time.
# usage: python read_cryotempo_points.py ./input/path/*.nc -o /output/path/dir -n 4
# undo: functions for reading the other type of cryotempo data.

import os
import h5py
import argparse
import pandas as pd
import netCDF4 as nc
from astropy.time import Time
from joblib import Parallel, delayed
from astropy.time import Time

### convert time (second format) to decimal year
def second_to_dyr(time_second, time_start='2000-01-01 00:00:00.0'):
    ''' this function suitable for the jason data, sentinel-3 data,
        and the cryosat2 data for time conversion.
    '''
    second_start = Time(time_start) ## the start of the second time, some case should be 1970.1.1
    second_start_gps = Time(second_start, format="gps").value  ## seconds that elapse since gps time.
    time_start = time_second + second_start_gps    ## seconds between time_start and gps time + seconds between gps time and the given time_second.
    time_start_gps = Time(time_start, format="gps")
    time_second_dyr = Time(time_start_gps, format="decimalyear").value
    return time_second_dyr

def get_args():
    description = "read cryotempo eolis point data files."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(         
            "ifiles", metavar="ifiles", type=str, nargs="+",
            help="input files to read (.nc).")
    parser.add_argument(           
            '-o', metavar=('outdir'), dest='outdir', type=str, nargs=1,
            help='path to output folder', 
            default=[""])
    parser.add_argument(
            "-n", metavar=("njobs"), dest="njobs", type=int, nargs=1,
            help="number of cores to use for parallel processing", 
            default=[1])
    return parser.parse_args()

def read_cryotempo_points(file_in, dir_out):

  data = {}   # convert .nc data to dictionary format.
  with nc.Dataset(file_in) as netcdf:
      for column in netcdf.variables:
          rows_from_nc = netcdf.variables[column]
          data[column] = pd.Series(rows_from_nc[:])
  df = pd.DataFrame(data)

  time_dyr = second_to_dyr(df['time'].values, time_start='1970-01-01')
  df.time = time_dyr  ### convert second format time to decimal time.
  data_dict = df.to_dict(orient='list')

  #------------------------------------------#
  # Writting out the selected data        #
  #------------------------------------------#
  name, _ = os.path.splitext(os.path.basename(file_in))
  file_out = os.path.join(dir_out, name + "_" + "readout.h5")
  with h5py.File(file_out, "w") as f_out:
      [f_out.create_dataset(key, data=data_dict[key]) for key in  data_dict.keys()]
  print('written file:', file_out)

  return

if __name__ == '__main__':

    ### ---- read input from command line
    args = get_args()
    ifiles = args.ifiles
    dir_out = args.outdir[0]
    njobs = args.njobs[0]

    if njobs == 1:
        print("running in serial ...")
        [read_cryotempo_points(f, dir_out) for f in ifiles]
    else:
        print(("running in parallel (%d jobs) ..." % njobs))
        Parallel(n_jobs=njobs, verbose=5)(
            delayed(read_cryotempo_points)(f, dir_out) for f in ifiles)


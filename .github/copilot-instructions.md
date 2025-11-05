# AI Coding Agent Instructions

## Project Overview
This is a radar altimetry data processing toolbox for Sentinel-3, Jason-1/2/3, CryoSat-2, and other satellite altimetry missions (excluding SWOT). The project follows a two-tier architecture:

- **`notebook/`**: Interactive workflows demonstrating data processing pipelines
- **`utils/`**: Core processing functions and command-line tools

## Data Processing Architecture

### Time Convention System
**CRITICAL**: All missions use different time reference systems that must be converted to decimal year format:
- **Sentinel-3**: Uses datetime64 → convert via `dt64_to_dyr()`
- **CryoSat-2/Jason**: Uses seconds since epoch → convert via `second_to_dyr(time_second, time_start)`
- Time start epochs vary: '2000-01-01' (CryoSat), '1970-01-01' (CryoTempo), GPS time for others

### Data Frequency Patterns
Altimetry data operates on **dual-frequency system**:
- **1Hz data**: Geophysical corrections, metadata (lower resolution)
- **20Hz data**: Waveforms, elevations, coordinates (higher resolution)
- Use `hz01_hz20()` from `utils.py` for temporal interpolation between frequencies

### File Processing Pipeline
1. **Input**: NetCDF4 (.nc) files from various missions
2. **Processing**: Extract variables → Apply corrections → Temporal conversions
3. **Output**: HDF5 (.h5) files with standardized variable naming
4. **Parallel**: Use `joblib.Parallel` with `-n` parameter for multi-core processing

## Mission-Specific Patterns

### Sentinel-3
- **File structure**: `.SEN3/enhanced_measurement.nc`
- **Key variables**: `lat_20_ku`, `lon_20_ku`, `elevation_ocog_20_ku`, `waveform_20_ku`
- **Corrections**: Geoid, tropospheric, ionospheric, tidal corrections from 1Hz data
- **Retracking**: Manual waveform retracking using gate positions (typically ~43-55 gates)

### CryoSat-2
- **GOPM**: Geophysical Ocean Product (LRM mode)
- **SIN**: SARIn mode for land ice
- **SAR**: SAR mode for ocean/ice
- **CryoTempo-EOLIS**: Swath processing for elevation points

### Jason Series
- **Variable patterns**: Follow NASA/CNES naming conventions
- **Corrections**: Standard oceanic corrections at 1Hz, interpolated to 20Hz

## Development Workflows

### Command-Line Tools
All utils support standard patterns:
```bash
python read_s3l2.py data/**/*.nc -n 4           # Parallel processing
python read_cryotempo.py input/*.nc -o output/  # Output directory
python merge_files.py files_*.h5 -o merged.h5 -m 5  # Merge with compression
```

### Notebook Environment
- Use `venv-altimetry` kernel environment
- Import pattern: `from pyrsimg import readTiff, imgShow, second_to_dyr`
- Visualization: `cartopy.crs` for map projections, scatter plots for track visualization
- Always load corresponding remote sensing background images for spatial context

### GDAL Integration
`commands_gdal.sh` provides essential raster operations:
- **Resampling**: `-tr 1000 1000 -r average` for 1km resolution
- **Compression**: Always use `-co COMPRESS=LZW`
- **Subsetting**: `-projwin extent` for geographic bounds
- **Mosaicking**: `gdal_merge.py` with `-n -999` for nodata handling

## Code Conventions

### Variable Naming
- **Coordinates**: `lat_20_ku`, `lon_20_ku` (frequency_band format)
- **Time**: `time_20_ku` → convert to decimal year as `time_dyr`
- **Elevations**: `elevation_ocog_20_ku` (algorithm_frequency_band)
- **Corrections**: Prefix with mission-specific identifiers

### File Organization
- **Data files**: Store in `data/{mission}/` subdirectories
- **Processing outputs**: Generate descriptive filenames with `_readout.h5` suffix
- **Temporary files**: Use `z_tmp.ipynb` for experimental work

### Error Handling
- Always check data validity before processing (NaN handling)
- Use `np.argmin(abs(coordinate_difference))` for nearest-neighbor matching
- Validate geophysical corrections are reasonable (-100m to +100m typically)

## External Dependencies
- **Core**: `xarray`, `netCDF4`, `h5py`, `numpy`, `astropy.time`
- **Visualization**: `matplotlib`, `cartopy`
- **Image processing**: `pyrsimg` (custom remote sensing library)
- **Parallel**: `joblib` for multi-core processing
- **Geospatial**: GDAL tools for raster operations

## Key Integration Points
- **Waveform retracking**: Manual gate selection requires domain knowledge of return signal characteristics
- **Geophysical corrections**: Mission-specific correction models must be applied in proper sequence
- **Coordinate systems**: WGS84 with various geoid models (EGM96/EGM2008) depending on mission
- **Quality control**: Always visualize tracks overlaid on remote sensing imagery for validation
#This repository contains multiple .sh and .py files with different purposes in the Sol and EEMT calculations:

##Python (.py) files

###Tiff.py
####Designed to import DAYMET and PRISM .tif images, calculate their region, merge, and warp
###eemt.py
####example scripts, not implemented yet.
###eemt_workqueue.py
####WorkQueue file that specifies the import and output files for calculating r.sun 
###gdal_merge.py
####Module to extract data from many rasters into one output, Author: Frank Warmerdam
###parser.py
####Reads DEM.tif file info via gdalinfo command, determines the projection zone and region of the .tif, convertsto DAYMET projection
###process_dem.py
####Example scripts, not implemented yet. 
###read_meta.py
####Example scripts, not implemented yet.
###tiffparser.py
####Example scripts, not implemented yet.

##Module files
###czorc
####Module file for setting paths to GRASS, PYTHON, and LIBRARY in a Bash shell
###czorc_csh
####Module file for setting paths to GRASS, PYTHON, and LIBRARY in a csh shell

##Shell (.sh) files
###iget_daymet.sh
####Shell file for calling the monhtly averaged DAYMET data from the iPlant Datastore 
###install_dep.sh
####List of all dependencies with installation commands
###r.eemt.sh
####Shell file containing the raster map calculations for producing EEMT-Topo and EEMT-Trad
###rmean.sh
####Shell file for calculating the sum, average, median, standard deviation, and variance of the daily r.sun outputs
###rsun.sh
####Shell file for calculating daily global solar radiation and hours of sun per day; also calculates direct solar radiation of all points using flat surfaces

##Distributed files
###r.eemt.distributed
####WorkQueue master for generating EEMT, executes using all of the shell files in the repository 
###r.series.distributed
####Workqueue master for calculating the r.sun statistics with rmean.sh
###r.sun.distributed
####WorkQueue master for calculating daily solar radiation. 

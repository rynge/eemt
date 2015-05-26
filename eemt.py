#!/usr/bin/env python

import sys
import os
import argparse
import getpass
import datetime
import calendar
import glob
import math, decimal
import tarfile
import urllib
import eemt_workqueue
from os.path import expanduser
from subprocess import Popen, PIPE
from shutil import copy
from Tiff import Tiff


DAYMET_URL="http://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/1219/tiles/"
DAYMET_PARAMS=["tmin","tmax","prcp"]

def main():

    os.chdir("/home/posideon/professional/CZO/data/south_southern_sierra_snow_off/pitRemove")
    test=Tiff("","pit.tif")

##--Default Values 
    base_year=1980
    final_year=datetime.date.today().year - 2
    input_dir="./"
    output_dir="./"
    proj_name=getpass.getuser()
    run_dir=os.getcwd();
    files=['pitRemove.tar.gz','TWI.tar.gz']
    tiffs=list()
##--Set up command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_year", type=int, default=1980, help="The year in which you would like to start calculating EEMT for. Must be greater than 1980. Defaults to 1980")
    parser.add_argument("-e", "--end_year", type=int, default=final_year, help="The year in which you would like to end calculating EEMT. Must be less than the current year - 1")
    parser.add_argument("-i", "--input", default=input_dir, help="The directory where the input files are stored. Defaults to current directory")
    parser.add_argument("-o", "--output", default=output_dir, help="Directory where the output EEMTs will be stored. Defaults to current directory")
    parser.add_argument("-n", "--name", default=proj_name,help="Project name to use for workqueue and output. Defaults to current username")
    parser.add_argument("-t","--topo",action="store_true" , help="Calculate Topographical EEMT")
    parser.add_argument("-v","--topo_veg",action="store_true" , help="Calculate Topo-Veg EEMT")  
    args = parser.parse_args()
##--Check arguments
    if args.start_year < base_year:
        sys.exit("Start Year must be greater than 1980")
    if args.end_year > final_year:
        sys.exit("End Year must be less than current year - 1")
    if not os.path.isdir(args.input):
        sys.exit("Input directory \"" + args.output + "\" does not exist or does not have correct permissions")
    if not os.path.isdir(args.output):
        sys.exit("Output directory \"" + args.output + "\" does not exist or does not have correct permissions")
##--Confirm values with user
    print "Confirm run EEMT with these settings: "
    print "  Start Year: " + `args.start_year`
    print "  End Year: " + `args.end_year`
    print "  Input Directory: " + args.input
    print "  Output Directory: " + args.output
    print "  Topographical EEMT: " + `args.topo`
    print "  Topo-Veg EEMT: " + `args.topo_veg`
    print "  Project Name: " + args.name
    conf=raw_input("Press [n\N] to cancel or any key to begin")
    if conf=="n" or conf=="N":
        sys.exit("User quit")
        
##--Start Main Program
##--Create temp directory     
    proj_dir=create_temp_directory()

##--Extract input files into the temp directory
    extract_files(args.input, proj_dir, files)
##--Retrieve NA_DEM
    get_na_dem(args.input, proj_dir)
##--Load input tiffs
    twi,pit,na_dem = load_tiffs(proj_dir, tiffs)
    wq=eemt_workqueue.init_workqueue(proj_dir, 9123, "CALLAHAN")
    wq,tasks = eemt_workqueue.create_tasks_eemt_topo(wq, proj_dir)
    print "Number of Tasks submitted: %d" % tasks
    eemt_workqueue.run(wq,tasks)
    quit()
##--Download DAYMET Files
    get_dayment_files(DAYMET_PARAMS, twi.tiles, args.start_year, args.end_year, proj_dir)
##--Convert DAYMET files from *.nc to *.tif

    return
def extract_files(input_dir, project_dir, files):
    print "Extracting OpenTopo DEMS"
    for file_name in files:
        file_path=os.path.join(input_dir,file_name)
        print file_path
        if os.path.isfile(file_path):
            print "  Extracting " + file_name
            tfile=tarfile.open(file_path,'r:gz')
            tfile.extractall(project_dir)
    return
def create_temp_directory():
    print "Creating Project Directory"
    home=expanduser("~")
    minute=datetime.datetime.now().minute
    if datetime.datetime.now().minute < 10:
        minute="0" + `datetime.datetime.now().minute`
    minute=str(minute)
    temp_dir=home+"/sol_data/"+`datetime.datetime.now().day`+calendar.month_abbr[datetime.datetime.now().month]+`datetime.datetime.now().year`+":"+`datetime.datetime.now().hour`+minute
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    else:
        print "Directory already exists"
    print "Project Working Directory is " + temp_dir
    return temp_dir
def get_na_dem(input_dir,project_dir):
    na_dem_path=os.path.join(input_dir,"na_dem.tif")
    na_dem_project_path=os.path.join(project_dir,"na_dem.tif")
    if not os.path.isfile(na_dem_path):
        print "na_dem.tif not found in input directory: " + input_dir + "."
        print "Downloading na_dem.tif from remote source not yet implemented. Exiting"
        sys.exit(1)
        print "Now downloading na_dem.tif..."
        #TODO
        #DOWNLOAD NA_DEM
        #COPY NA_DEM TO PROJECT DIRECTORY
        #CLIP NA_DEM
    else:
        print "na_dem.tif found in input directory. Copying to project directory"
        copy(na_dem_path,na_dem_project_path)
        print "Done."
    return  
def load_tiffs(proj_dir, tiffs):
##--Get all the files in the project directory needed - grouped into like files
##--felps==pitRemove
##--twis==TWI DEMS
    felps_names=glob.glob(os.path.join(proj_dir,"felp*.tif"))
    twis_names=glob.glob(os.path.join(proj_dir,"twi*.tif"))
##--Convert to Tiff objects
    twis=list()
    felps=list()
    for tif in twis_names:
        temp = Tiff(proj_dir,tif)
        twis.append(temp)
    for tif in felps_names:
        temp = Tiff(proj_dir,tif)
        felps.append(temp)
##--Merge each type into 1 file
    twi_1=twis.pop(0)
    felp_1=felps.pop(0)
    pit=felp_1.mergeTiff(felps,proj_dir,"pit.tif")
    twi=twi_1.mergeTiff(twis,proj_dir,"twi.tif")
##--Warp files
    pit.warp("DAYMET")
    pit_c=Tiff(proj_dir,pit.filename[:-4]+"_converted.tif")
    twi.warp("DAYMET")
    twi_c=Tiff(proj_dir,twi.filename[:-4]+"_converted.tif")
##--Load the na_dem
    coords=pit_c.getProjCoords()
    ul = [str(math.floor(decimal.Decimal(coords[1][0]) / 1000) * 1000), str(math.ceil(decimal.Decimal(coords[1][1]) / 1000) * 1000)]
    lr = [str(math.ceil(decimal.Decimal(coords[0][0]) / 1000) * 1000), str(math.floor(decimal.Decimal(coords[0][1]) / 1000) * 1000)]
    command = ['gdal_translate', '-projwin', ul[0], ul[1], lr[0], lr[1], os.path.join(proj_dir, 'na_dem.tif'), os.path.join(proj_dir, 'na_dem.part.tif')]
    print "Partitioning na_dem"
    process=Popen(command,stdout=PIPE,shell=False)
    process.communicate()
    if process.returncode != 0:
        sys.exit("Failed to partition na_dem\n")
    print "na_dem successfully partitioned"
    na_dem =Tiff(proj_dir,"na_dem.part.tif")
    return twi_c, pit_c, na_dem
def get_dayment_files(params,tiles,start,end,proj_dir):
    for tile in tiles:         
        for i in range(0,end-start+1):            
            year = start+i
            print "Downloading DAYMET information for tile " + `tile` + " for the year " + `year`
            for param in params:
                print "     Downloading " + param + " data from DAYMET"
                param_url=DAYMET_URL+`year`+"/"+`tile`+"_"+`year`+"/"+param+".nc"
                out = urllib.urlretrieve(param_url,os.path.join(proj_dir,param+".nc"))
    print "All DAYMET data downloaded"
    return
if __name__ == '__main__':
    main()

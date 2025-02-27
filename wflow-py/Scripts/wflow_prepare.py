#!python
"""
wflow_prepare
=============

wflow data preparation script. Data preparation can be done by hand or using 
the two scripts. This script does the first step. The second  step does 
the resampling. This scripts need the pcraster and gdal executables to be
available in you search path.


Usage::

    wflow_prepare_step1 [-W workdir][-f][-h] -I inifile 
    
    -f force recreation of ldd if it already exists
    -h show this information
    -W set the working directory, default is current dir
    -I name of the ini file with settings
            
$Id: $  


.. todo:
    # Add a legend to the maps
    # possibility to give a file with gauge names (legend)
    # add shape files and qgis config for easy viewing
    
.. todo:
    # calibration script
    
.. todo:
    # plotting functions in python
    # reporting in python
"""

try:
    import wflow.wflow_lib as tr
except ImportError:
    import wflow_lib as tr

import os
import os.path
import getopt
import ConfigParser
import sys
import gc


def usage(*args):
    sys.stdout = sys.stderr
    for msg in args:
        print msg
    print __doc__
    sys.exit(0)


def configget(config, section, var, default):
    """
    gets parameter from config file and returns a default value
    if the parameter is not found
    """
    try:
        ret = config.get(section, var)
    except:
        print "returning default (" + default + ") for " + section + ":" + var
        ret = default

    return ret


def OpenConf(fn):
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str

    if os.path.exists(fn):
        config.read(fn)
    else:
        print "Cannot open config file: " + fn
        sys.exit(1)

    return config


def mkoutputdirs(step1dir, step2dir):
    """
    creates the outputdirs
    """
    # make the directories to save results in
    if not os.path.isdir(step1dir + "/"):
        os.makedirs(step1dir)
    if not os.path.isdir(step2dir):
        os.makedirs(step2dir)


def readdem(initialscale, masterdem, step1dir):
    """    
    """
    if initialscale > 1:
        print "Initial scaling of DEM..."
        os.system(
            "resample -r "
            + str(initialscale)
            + " "
            + masterdem
            + " "
            + step1dir
            + "/dem_scaled.map"
        )
        print ("Reading dem...")
        dem = tr.readmap(step1dir + "/dem_scaled.map")
        ldddem = dem
    else:
        print ("Reading dem...")
        dem = tr.readmap(masterdem)
        ldddem = dem

    return ldddem


def resamplemaps(step1dir, step2dir):
    """
    Resample the maps from step1 and rename them in the process
    """
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem10.map "
        + step2dir
        + "/wflow_dem10.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem25.map "
        + step2dir
        + "/wflow_dem25.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem33.map "
        + step2dir
        + "/wflow_dem33.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem50.map "
        + step2dir
        + "/wflow_dem50.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem66.map "
        + step2dir
        + "/wflow_dem66.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem75.map "
        + step2dir
        + "/wflow_dem75.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/dem90.map "
        + step2dir
        + "/wflow_dem90.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/demavg.map "
        + step2dir
        + "/wflow_dem.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/demmin.map "
        + step2dir
        + "/wflow_demmin.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/demmax.map "
        + step2dir
        + "/wflow_demmax.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/riverlength_fact.map "
        + step2dir
        + "/wflow_riverlength_fact.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/catchment_overall.map "
        + step2dir
        + "/catchment_cut.map"
    )
    os.system(
        "resample --clone "
        + step2dir
        + "/cutout.map "
        + step1dir
        + "/rivers.map "
        + step2dir
        + "/wflow_riverburnin.map"
    )


def main():
    """
        
    :ivar masterdem: digital elevation model
    :ivar dem: digital elevation model
    :ivar river: optional river map
    """

    # Default values
    strRiver = 8
    masterdem = "dem.map"
    step1dir = "step1"
    step2dir = "step2"
    workdir = "."
    inifile = "wflow_prepare.ini"
    recreate = False
    snapgaugestoriver = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "W:hI:f")
    except getopt.error, msg:
        usage(msg)

    for o, a in opts:
        if o == "-W":
            workdir = a
        if o == "-I":
            inifile = a
        if o == "-h":
            usage()
        if o == "-f":
            recreate = True

    tr.setglobaloption("unitcell")
    os.chdir(workdir)

    config = OpenConf(workdir + "/" + inifile)

    masterdem = configget(config, "files", "masterdem", "dem.map")
    tr.setclone(masterdem)

    strRiver = int(configget(config, "settings", "riverorder", "4"))

    try:
        gauges_x = config.get("settings", "gauges_x")
        gauges_y = config.get("settings", "gauges_y")
    except:
        print "gauges_x and  gauges_y are required entries in the ini file"
        sys.exit(1)

    step1dir = configget(config, "directories", "step1dir", "step1")
    step2dir = configget(config, "directories", "step2dir", "step2")
    # upscalefactor = float(config.get("settings","upscalefactor"))

    corevolume = float(configget(config, "settings", "corevolume", "1E35"))
    catchmentprecipitation = float(
        configget(config, "settings", "catchmentprecipitation", "1E35")
    )
    corearea = float(configget(config, "settings", "corearea", "1E35"))
    outflowdepth = float(configget(config, "settings", "lddoutflowdepth", "1E35"))

    initialscale = int(configget(config, "settings", "initialscale", "1"))
    csize = float(configget(config, "settings", "cellsize", "1"))

    snapgaugestoriver = bool(
        int(configget(config, "settings", "snapgaugestoriver", "1"))
    )
    lddglobaloption = configget(config, "settings", "lddglobaloption", "lddout")
    tr.setglobaloption(lddglobaloption)
    lu_water = configget(config, "files", "lu_water", "")
    lu_paved = configget(config, "files", "lu_paved", "")

    # X/Y coordinates of the gauges the system
    exec "X=tr.array(" + gauges_x + ")"
    exec "Y=tr.array(" + gauges_y + ")"

    tr.Verbose = 1

    # make the directories to save results in
    mkoutputdirs(step1dir, step2dir)

    ldddem = readdem(initialscale, masterdem, step1dir)
    dem = ldddem

    try:
        catchmask = config.get("files", "catchment_mask")
    except:
        print "No catchment mask..."
    else:
        print "clipping DEM with mask....."
        mask = tr.readmap(catchmask)
        ldddem = tr.ifthen(tr.boolean(mask), ldddem)
        dem = tr.ifthen(tr.boolean(mask), dem)

    # See if there is a shape file of the river to burn in
    try:
        rivshp = config.get("files", "river")
    except:
        print "no river file specified"
        outletpointX = float(configget(config, "settings", "outflowpointX", "0.0"))
        outletpointY = float(configget(config, "settings", "outflowpointY", "0.0"))
    else:
        print "river file specified....."
        try:
            outletpointX = float(configget(config, "settings", "outflowpointX", "0.0"))
            outletpointY = float(configget(config, "settings", "outflowpointY", "0.0"))
        except:
            print (
                "Need to specify the river outletpoint (a point at the end of the river within the current map)"
            )
            exit(1)

        outletpointmap = tr.points_to_map(dem, outletpointX, outletpointY, 0.5)
        tr.report(outletpointmap, step1dir + "/outletpoint.map")
        rivshpattr = config.get("files", "riverattr")
        tr.report(dem * 0.0, step1dir + "/nilmap.map")
        thestr = (
            "gdal_translate -of GTiff "
            + step1dir
            + "/nilmap.map "
            + step1dir
            + "/riverburn.tif"
        )
        os.system(thestr)
        os.system(
            "gdal_rasterize -burn 1 -l "
            + rivshpattr
            + " "
            + rivshp
            + " "
            + step1dir
            + "/riverburn.tif"
        )
        thestr = (
            "gdal_translate -of PCRaster "
            + step1dir
            + "/riverburn.tif "
            + step1dir
            + "/riverburn.map"
        )
        os.system(thestr)
        riverburn = tr.readmap(step1dir + "/riverburn.map")
        # Determine regional slope assuming that is the way the river should run
        tr.setglobaloption("unitcell")
        demregional = tr.windowaverage(dem, 100)
        ldddem = tr.ifthenelse(riverburn >= 1.0, demregional - 1000, dem)

    tr.setglobaloption("unittrue")
    upscalefactor = int(csize / tr.celllength())

    print ("Creating ldd...")
    ldd = tr.lddcreate_save(
        step1dir + "/ldd.map",
        ldddem,
        recreate,
        outflowdepth=outflowdepth,
        corevolume=corevolume,
        catchmentprecipitation=catchmentprecipitation,
        corearea=corearea,
    )

    print ("Determining streamorder...")
    stro = tr.streamorder(ldd)
    tr.report(stro, step1dir + "/streamorder.map")
    strdir = tr.ifthen(stro >= strRiver, stro)
    tr.report(strdir, step1dir + "/streamorderrive.map")
    tr.report(tr.boolean(tr.ifthen(stro >= strRiver, stro)), step1dir + "/rivers.map")

    tr.setglobaloption("unittrue")
    # outlet (and other gauges if given)
    # TODO: check is x/y set if not skip this
    print ("Outlet...")

    outlmap = tr.points_to_map(dem, X, Y, 0.5)

    if snapgaugestoriver:
        print "Snapping gauges to nearest river cells..."
        tr.report(outlmap, step1dir + "/orggauges.map")
        outlmap = tr.snaptomap(outlmap, strdir)

    # noutletmap = tr.points_to_map(dem,XX,YY,0.5)
    # tr.report(noutletmap,'noutlet.map')

    tr.report(outlmap, step1dir + "/gauges.map")

    # check if there is a pre-define catchment map
    try:
        catchmask = config.get("files", "catchment_mask")
    except:
        print "No catchment mask, finding outlet"
        # Find catchment (overall)
        outlet = tr.find_outlet(ldd)
        sub = tr.subcatch(ldd, outlet)
        tr.report(sub, step1dir + "/catchment_overall.map")
    else:
        print "reading and converting catchment mask....."
        os.system(
            "resample -r "
            + str(initialscale)
            + " "
            + catchmask
            + " "
            + step1dir
            + "/catchment_overall.map"
        )
        sub = tr.readmap(step1dir + "/catchment_overall.map")

    print ("Scatch...")
    sd = tr.subcatch(ldd, tr.ifthen(outlmap > 0, outlmap))
    tr.report(sd, step1dir + "/scatch.map")

    tr.setglobaloption("unitcell")
    print "Upscalefactor: " + str(upscalefactor)

    if upscalefactor > 1:
        gc.collect()
        print ("upscale river length1 (checkerboard map)...")
        ck = tr.checkerboard(dem, upscalefactor)
        tr.report(ck, step1dir + "/ck.map")
        tr.report(dem, step1dir + "/demck.map")
        print ("upscale river length2...")
        fact = tr.area_riverlength_factor(ldd, ck, upscalefactor)
        tr.report(fact, step1dir + "/riverlength_fact.map")

        # print("make dem statistics...")
        dem_ = tr.areaaverage(dem, ck)
        tr.report(dem_, step1dir + "/demavg.map")

        print ("Create DEM statistics...")
        dem_ = tr.areaminimum(dem, ck)
        tr.report(dem_, step1dir + "/demmin.map")
        dem_ = tr.areamaximum(dem, ck)
        tr.report(dem_, step1dir + "/demmax.map")
        # calculate percentiles
        order = tr.areaorder(dem, ck)
        n = tr.areatotal(tr.spatial(tr.scalar(1.0)), ck)
        #: calculate 25 percentile
        perc = tr.area_percentile(dem, ck, n, order, 25.0)
        tr.report(perc, step1dir + "/dem25.map")
        perc = tr.area_percentile(dem, ck, n, order, 10.0)
        tr.report(perc, step1dir + "/dem10.map")
        perc = tr.area_percentile(dem, ck, n, order, 50.0)
        tr.report(perc, step1dir + "/dem50.map")
        perc = tr.area_percentile(dem, ck, n, order, 33.0)
        tr.report(perc, step1dir + "/dem33.map")
        perc = tr.area_percentile(dem, ck, n, order, 66.0)
        tr.report(perc, step1dir + "/dem66.map")
        perc = tr.area_percentile(dem, ck, n, order, 75.0)
        tr.report(perc, step1dir + "/dem75.map")
        perc = tr.area_percentile(dem, ck, n, order, 90.0)
        tr.report(perc, step1dir + "/dem90.map")
    else:
        print ("No fancy scaling done. Going strait to step2....")
        tr.report(dem, step1dir + "/demavg.map")
        Xul = float(config.get("settings", "Xul"))
        Yul = float(config.get("settings", "Yul"))
        Xlr = float(config.get("settings", "Xlr"))
        Ylr = float(config.get("settings", "Ylr"))
        gdalstr = (
            "gdal_translate  -projwin "
            + str(Xul)
            + " "
            + str(Yul)
            + " "
            + str(Xlr)
            + " "
            + str(Ylr)
            + " -of PCRaster  "
        )
        # gdalstr = "gdal_translate  -a_ullr " + str(Xul) + " " + str(Yul) + " " +str(Xlr) + " " +str(Ylr) + " -of PCRaster  "
        print gdalstr
        tr.report(tr.cover(1.0), step1dir + "/wflow_riverlength_fact.map")
        # Now us gdat tp convert the maps
        os.system(
            gdalstr
            + step1dir
            + "/wflow_riverlength_fact.map"
            + " "
            + step2dir
            + "/wflow_riverlength_fact.map"
        )
        os.system(
            gdalstr + step1dir + "/demavg.map" + " " + step2dir + "/wflow_dem.map"
        )
        os.system(
            gdalstr + step1dir + "/demavg.map" + " " + step2dir + "/wflow_demmin.map"
        )
        os.system(
            gdalstr + step1dir + "/demavg.map" + " " + step2dir + "/wflow_demmax.map"
        )
        os.system(
            gdalstr + step1dir + "/gauges.map" + " " + step2dir + "/wflow_gauges.map"
        )
        os.system(
            gdalstr + step1dir + "/rivers.map" + " " + step2dir + "/wflow_river.map"
        )
        os.system(
            gdalstr
            + step1dir
            + "/streamorder.map"
            + " "
            + step2dir
            + "/wflow_streamorder.map"
        )
        os.system(
            gdalstr + step1dir + "/gauges.map" + " " + step2dir + "/wflow_outlet.map"
        )
        os.system(
            gdalstr + step1dir + "/scatch.map" + " " + step2dir + "/wflow_catchment.map"
        )
        os.system(gdalstr + step1dir + "/ldd.map" + " " + step2dir + "/wflow_ldd.map")
        os.system(
            gdalstr + step1dir + "/scatch.map" + " " + step2dir + "/wflow_subcatch.map"
        )

        if lu_water:
            os.system(gdalstr + lu_water + " " + step2dir + "/WaterFrac.map")

        if lu_paved:
            os.system(gdalstr + lu_paved + " " + step2dir + "/PathFrac.map")

        try:
            lumap = config.get("files", "landuse")
        except:
            print "no landuse map...creating uniform map"
            # clone=tr.readmap(step2dir + "/wflow_dem.map")
            tr.setclone(step2dir + "/wflow_dem.map")
            tr.report(tr.nominal(1), step2dir + "/wflow_landuse.map")
        else:
            os.system(
                "resample --clone "
                + step2dir
                + "/wflow_dem.map "
                + lumap
                + " "
                + step2dir
                + "/wflow_landuse.map"
            )

        try:
            soilmap = config.get("files", "soil")
        except:
            print "no soil map..., creating uniform map"
            tr.setclone(step2dir + "/wflow_dem.map")
            tr.report(tr.nominal(1), step2dir + "/wflow_soil.map")
        else:
            os.system(
                "resample --clone "
                + step2dir
                + "/wflow_dem.map "
                + soilmap
                + " "
                + step2dir
                + "/wflow_soil.map"
            )

    ##################################
    # Step 2 starts here
    ##################################

    tr.setclone(step2dir + "/cutout.map")

    strRiver = int(configget(config, "settings", "riverorder_step2", "4"))

    corevolume = float(configget(config, "settings", "corevolume", "1E35"))
    catchmentprecipitation = float(
        configget(config, "settings", "catchmentprecipitation", "1E35")
    )
    corearea = float(configget(config, "settings", "corearea", "1E35"))
    outflowdepth = float(configget(config, "settings", "lddoutflowdepth", "1E35"))
    lddmethod = configget(config, "settings", "lddmethod", "dem")
    lddglobaloption = configget(config, "settings", "lddglobaloption", "lddout")
    tr.setglobaloption(lddglobaloption)

    nrrow = round(abs(Yul - Ylr) / csize)
    nrcol = round(abs(Xlr - Xul) / csize)
    mapstr = (
        "mapattr -s -S -R "
        + str(nrrow)
        + " -C "
        + str(nrcol)
        + " -l "
        + str(csize)
        + " -x "
        + str(Xul)
        + " -y "
        + str(Yul)
        + " -P yb2t "
        + step2dir
        + "/cutout.map"
    )

    os.system(mapstr)
    tr.setclone(step2dir + "/cutout.map")

    lu_water = configget(config, "files", "lu_water", "")
    lu_paved = configget(config, "files", "lu_paved", "")

    if lu_water:
        os.system(
            "resample --clone "
            + step2dir
            + "/cutout.map "
            + lu_water
            + " "
            + step2dir
            + "/wflow_waterfrac.map"
        )

    if lu_paved:
        os.system(
            "resample --clone "
            + step2dir
            + "/cutout.map "
            + lu_paved
            + " "
            + step2dir
            + "/PathFrac.map"
        )

    #
    try:
        lumap = config.get("files", "landuse")
    except:
        print "no landuse map...creating uniform map"
        clone = tr.readmap(step2dir + "/cutout.map")
        tr.report(tr.nominal(clone), step2dir + "/wflow_landuse.map")
    else:
        os.system(
            "resample --clone "
            + step2dir
            + "/cutout.map "
            + lumap
            + " "
            + step2dir
            + "/wflow_landuse.map"
        )

    try:
        soilmap = config.get("files", "soil")
    except:
        print "no soil map..., creating uniform map"
        clone = tr.readmap(step2dir + "/cutout.map")
        tr.report(tr.nominal(clone), step2dir + "/wflow_soil.map")
    else:
        os.system(
            "resample --clone "
            + step2dir
            + "/cutout.map "
            + soilmap
            + " "
            + step2dir
            + "/wflow_soil.map"
        )

    resamplemaps(step1dir, step2dir)

    dem = tr.readmap(step2dir + "/wflow_dem.map")
    demmin = tr.readmap(step2dir + "/wflow_demmin.map")
    demmax = tr.readmap(step2dir + "/wflow_demmax.map")
    catchcut = tr.readmap(step2dir + "/catchment_cut.map")
    # now apply the area of interest (catchcut) to the DEM
    # dem=tr.ifthen(catchcut >=1 , dem)
    #

    # See if there is a shape file of the river to burn in
    try:
        rivshp = config.get("files", "river")
    except:
        print "no river file specified"
        riverburn = tr.readmap(step2dir + "/wflow_riverburnin.map")
    else:
        print "river file speficied....."
        rivshpattr = config.get("files", "riverattr")
        tr.report(dem * 0.0, step2dir + "/nilmap.map")
        thestr = (
            "gdal_translate -of GTiff "
            + step2dir
            + "/nilmap.map "
            + step2dir
            + "/wflow_riverburnin.tif"
        )
        os.system(thestr)
        os.system(
            "gdal_rasterize -burn 1 -l "
            + rivshpattr
            + " "
            + rivshp
            + " "
            + step2dir
            + "/wflow_riverburnin.tif"
        )
        thestr = (
            "gdal_translate -of PCRaster "
            + step2dir
            + "/wflow_riverburnin.tif "
            + step2dir
            + "/wflow_riverburnin.map"
        )
        os.system(thestr)
        riverburn = tr.readmap(step2dir + "/wflow_riverburnin.map")
        # ldddem = tr.ifthenelse(riverburn >= 1.0, dem -1000 , dem)

    # Only burn within the original catchment
    riverburn = tr.ifthen(tr.scalar(catchcut) >= 1, riverburn)
    # Now setup a very high wall around the catchment that is scale
    # based on the distance to the catchment so that it slopes away from the
    # catchment
    if lddmethod != "river":
        print "Burning in highres-river ..."
        disttocatch = tr.spread(tr.nominal(catchcut), 0.0, 1.0)
        demmax = tr.ifthenelse(
            tr.scalar(catchcut) >= 1.0,
            demmax,
            demmax + (tr.celllength() * 100.0) / disttocatch,
        )
        tr.setglobaloption("unitcell")
        demregional = tr.windowaverage(demmin, 100)
        demburn = tr.cover(
            tr.ifthen(tr.boolean(riverburn), demregional - 100.0), demmax
        )
    else:
        print "using average dem.."
        demburn = dem

    ldd = tr.lddcreate_save(
        step2dir + "/ldd.map",
        demburn,
        True,
        outflowdepth=outflowdepth,
        corevolume=corevolume,
        catchmentprecipitation=catchmentprecipitation,
        corearea=corearea,
    )

    # Find catchment (overall)
    outlet = tr.find_outlet(ldd)
    sub = tr.subcatch(ldd, outlet)
    tr.report(sub, step2dir + "/wflow_catchment.map")
    tr.report(outlet, step2dir + "/wflow_outlet.map")

    # make river map
    strorder = tr.streamorder(ldd)
    tr.report(strorder, step2dir + "/wflow_streamorder.map")

    river = tr.ifthen(tr.boolean(strorder >= strRiver), strorder)
    tr.report(river, step2dir + "/wflow_river.map")

    # make subcatchments
    # os.system("col2map --clone " + step2dir + "/cutout.map gauges.col " + step2dir + "/wflow_gauges.map")
    exec "X=tr.array(" + gauges_x + ")"
    exec "Y=tr.array(" + gauges_y + ")"

    tr.setglobaloption("unittrue")

    outlmap = tr.points_to_map(dem, X, Y, 0.5)
    tr.report(outlmap, step2dir + "/wflow_gauges_.map")

    if snapgaugestoriver:
        print "Snapping gauges to river"
        tr.report(outlmap, step2dir + "/wflow_orggauges.map")
        outlmap = tr.snaptomap(outlmap, river)

    outlmap = tr.ifthen(outlmap > 0, outlmap)
    tr.report(outlmap, step2dir + "/wflow_gauges.map")

    scatch = tr.subcatch(ldd, outlmap)
    tr.report(scatch, step2dir + "/wflow_subcatch.map")


if __name__ == "__main__":
    main()

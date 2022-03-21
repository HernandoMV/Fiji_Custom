# Hernando M. Vergara March 2022

# This scripts registers lesion ROIs to ARA

from ij import IJ
import glob
from os import path
import sys
sys.path.append(path.abspath(path.dirname(__file__)))
from ij.plugin.frame import RoiManager

ATLAS_RESOLUTION = float(25) # um/px

ROI_FILE_ENDING = '_lesionROI.zip'
REGISTRATION_COORDS_FILE_ENDING = '_ch0_Coords.tif'

# AP_OFFSET = - float(18) * 25 / 1000 # In mm
AP_OFFSET = 0.

ATLAS_FILE = '/home/hernandom/data/Anatomy/ARA_25_micron_mhd/template.tif'

def roi_to_ARA(roi, coords):
    # get ROI xy coordinates
    # roi_polygon = roi.getPolygon()
    # xs = roi_polygon.xpoints
    # ys = roi_polygon.ypoints
    # point_list = zip(xs,ys)
    point_list = roi.getContainedPoints()
    # find the ARA xyz coordinates
    xt = []
    yt = []
    zt = []
    for point in point_list:
        point_a = [point.x, point.y]
        z, y, x = ARAcoords_of_point(point_a, coords)
        # append
        xt.append(x)
        yt.append(y)
        zt.append(z)

    # get the points
    reg_filling = list(zip(xt, yt))

    # adjust offset
    ozt = [int(AP_OFFSET * 1000 / ATLAS_RESOLUTION) + z for z in zt]

    # start with z as the mean
    mean_z = int(sum(ozt)/len(ozt))

    return reg_filling, mean_z, ozt


def ARAcoords_of_point(point, coords):
    # order is ap, dv, ml
    reg_coords = []
    for i in range(1,4):
        coords.setSlice(i)
        ip = coords.getProcessor()
        coord = ip.getPixelValue(point[0], point[1])
        # Convert to pixel coordinates and append
        sc_c = int(coord * 1000 / ATLAS_RESOLUTION)

        reg_coords.append(sc_c)

    return reg_coords[0], reg_coords[1], reg_coords[2]


def paint_reg_roi(registered_roi, sample_im, mask_name):
    # create new
    imp = IJ.createImage("roi_mask_" + mask_name, "8-bit black", sample_im.getWidth(), sample_im.getHeight(), 1)
    ip = imp.getProcessor()
    # paint pixels
    for pixel in registered_roi:
        ip.set(pixel[0], pixel[1], 255)
    # erode and dilate to clean 
    IJ.run(imp, "Erode", "")
    IJ.run(imp, "Dilate", "")

    return imp


def roi_from_mask(mask, coords_im, mask_name):
    # paint the points in a new image to see how well reconstituted it is
    imp = paint_reg_roi(mask, coords_im, mask_name)
    imp.show()
    imp_tit = imp.getTitle()
    rm = RoiManager()
    IJ.selectWindow(imp_tit)
    mask = IJ.getImage()
    IJ.setThreshold(mask, 1, 255)
    IJ.run(mask, "Create Selection", "")
    IJ.selectWindow(imp_tit)
    rm.runCommand("add")
    IJ.selectWindow(imp_tit)
    IJ.run("Close")
    roi = rm.getRoi(0)
    rm.close()
    
    return roi


def paint_atlas(imp, roi, slice_num):
    ip = imp.getProcessor()
    pixels = roi.getContainedPoints()
    for idx, point in enumerate(pixels):
        imp.setSlice(slice_num)
        ip.set(point.x, point.y, 255)


# Main
if __name__ in ['__builtin__', '__main__']:
    IJ.run("Close All")
    # get a directory and find the list of candidate ROIs
    input_path= IJ.getDirectory('choose a path containing your ROIs')
    candidate_ROIs = []
    for file in glob.glob(input_path + '*' + ROI_FILE_ENDING):
        candidate_ROIs.append(file)

    # check that it has its slice has been registered
    ROIs_to_process = []
    for roi in candidate_ROIs:
        coords_file = roi.split(ROI_FILE_ENDING)[0] + REGISTRATION_COORDS_FILE_ENDING
        if not path.exists(coords_file):
            print('No registration file found for ROI {}'.format(path.basename(roi)))
        else:
            ROIs_to_process.append(roi)
    
    # list to store the registered ROIs:
    registered_rois = []
    # open the ROIs and add it to the manager
    for file_idx, ROI in enumerate(ROIs_to_process):
        print('Registering {}'.format(path.basename(ROI)))
        # open roi manager
        rm = RoiManager()
        # load the regions file
        rm.runCommand("Open", ROI)
        # get the number of ROIs in the file
        rois_number = rm.getCount()
        # open the coords file
        coords_file = ROI.split(ROI_FILE_ENDING)[0] + REGISTRATION_COORDS_FILE_ENDING
        coords_im = IJ.openImage(coords_file)
        # coords_im.show()

        filling_list = []
        names = []
        for roi_index in range(rois_number):
            roi_to_register = rm.getRoi(roi_index)
            # get name
            roi_name = rm.getName(roi_index)
            # paint the roi, register the points, and reconstitute a ROI
            registered_fill, ap_position, all_zs = roi_to_ARA(roi_to_register, coords_im)
            # add the z location in the name
            names.append(roi_name+'-reg_z-'+str(ap_position))
            # rm.addRoi(registered_roi)
            filling_list.append(registered_fill)

        rm.close()
        coords_im.flush()

        # append them to list
        for idx, mask in enumerate(filling_list):
            # create a ROI out of it
            mask_idx = str(file_idx) + '-' + str(idx)
            reg_roi = roi_from_mask(mask, coords_im, mask_idx)
            reg_roi.setName(names[idx])
            # append to list
            registered_rois.append(reg_roi)
        
    # add them to roimanager in the atlas

    rm = RoiManager()
    atlas = IJ.openImage(ATLAS_FILE)
    IJ.run(atlas, "Reverse", "")
    atlas.show()
    # create a new stack to paint the rois
    pa_im = IJ.createImage("painted_atlas", "8-bit black", atlas.getWidth(), atlas.getHeight(), atlas.getNSlices())

    for roi in registered_rois:
        r_name = roi.getName()
        if 'lesion-reg_z-' in r_name:
            slice_num = int(r_name.split('-')[-1])
            # atlas.setSliceWithoutUpdate(slice_num)
            roi.setPosition(slice_num)
            rm.addRoi(roi)
            paint_atlas(pa_im, roi, slice_num)
        
    pa_im.show()

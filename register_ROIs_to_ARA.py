# Hernando M. Vergara March 2022

# This scripts registers lesion ROIs to ARA
# DO IT ONLY IN 2D FOR NOW!

from ij import IJ, ImagePlus
from ij.gui import Plot, Overlay, Roi, PolygonRoi
import glob
from os import path
import sys
sys.path.append(path.abspath(path.dirname(__file__)))
from ij.plugin.frame import RoiManager
from ij.process import FloatProcessor

ROI_FILE_ENDING = '_lesionROI.zip'
REGISTRATION_COORDS_FILE_ENDING = '_ch0_Coords.tif'

def roi_to_ARA(roi, coords):
    # get ROI xy coordinates

    # find the ARA xyz coordinates
    print('{} done'.format(roi.getName()))

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
    
    # open the ROIs and add it to the manager
    for ROI in ROIs_to_process:
        print('Registering {}'.format(path.basename(ROI)))
        # open roi manager
        rm = RoiManager()
        # load the regions file
        rm.runCommand("Open", ROI)
        # get the number of ROIs in the file
        rois_number = rm.getCount()
        # open the coords file
        coords_file = roi.split(ROI_FILE_ENDING)[0] + REGISTRATION_COORDS_FILE_ENDING
        coords_im = IJ.openImage(coords_file)
        coords_im.show()

        for roi_index in range(rois_number):
            roi_to_register = rm.getRoi(roi_index)
            registered_roi = roi_to_ARA(roi_to_register, coords_im)

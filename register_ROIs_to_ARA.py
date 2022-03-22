# Hernando M. Vergara March 2022

# This scripts registers lesion ROIs to ARA

from ij import IJ
from ij.plugin.frame import RoiManager
import glob
from os import path
import sys
sys.path.append(path.abspath(path.dirname(__file__)))
from functions.roi_and_ov_manipulation import roi_to_ARA
from functions.image_manipulation import roi_from_mask, paint_atlas, save_interpolated
from functions.text_manipulation import get_lesion_coord_file

ATLAS_RESOLUTION = float(25) # um/px

ROI_FILE_ENDING = '_lesionROI.zip'
REGISTRATION_COORDS_FILE_ENDING = '_ch0_Coords.tif'

# AP_OFFSET = - float(18) * 25 / 1000 # In mm
AP_OFFSET = 0.

ATLAS_FILE = '/home/hernandom/data/Anatomy/ARA_25_micron_mhd/template.tif'
ATLAS_FILE = r'C:\Users\herny\Desktop\SWC\Data\Anatomy\ARA_25_micron_mhd\template.tif'


# Main
if __name__ in ['__builtin__', '__main__']:
    IJ.run("Close All")
    # get a directory and find the list of candidate ROIs
    input_path= IJ.getDirectory('choose a path containing your ROIs')
    # define the output directory as the parent directory
    output_path = path.dirname(path.dirname(input_path))
    # get the name of the mouse
    mouse_name = path.basename(output_path)
    print('Analysing mouse {}'.format(mouse_name))
    # check if the registered image folder is there
    res = input_path.split('_')[-1]
    reg_path = path.join(output_path, 'Registration',
                         'Slices_for_ARA_registration_' + res)
    if path.exists(reg_path):
        print('Found registration output path.')
    else:
        sys.exit('No registration folder found')
        
    candidate_ROIs = []
    for file in glob.glob(input_path + '*' + ROI_FILE_ENDING):
        candidate_ROIs.append(file)

    # check that this slice has been registered
    ROIs_to_process = []
    for roi in candidate_ROIs:
        coords_file = get_lesion_coord_file(roi, ROI_FILE_ENDING,
                                            REGISTRATION_COORDS_FILE_ENDING, reg_path)
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
        coords_file = get_lesion_coord_file(ROI, ROI_FILE_ENDING,
                                            REGISTRATION_COORDS_FILE_ENDING, reg_path)
        coords_im = IJ.openImage(coords_file)
        # coords_im.show()

        filling_list = []
        names = []
        for roi_index in range(rois_number):
            roi_to_register = rm.getRoi(roi_index)
            # get name
            roi_name = rm.getName(roi_index)
            # paint the roi, register the points, and reconstitute a ROI
            registered_fill, ap_position, all_zs = roi_to_ARA(roi_to_register, coords_im,
                                                              ATLAS_RESOLUTION, AP_OFFSET)
            # add the z location in the name
            names.append(roi_name+'-reg_z-'+str(ap_position))
            # rm.addRoi(registered_roi)
            filling_list.append(registered_fill)

        rm.close()

        # append them to list
        for idx, mask in enumerate(filling_list):
            # create a ROI out of it
            mask_idx = str(file_idx) + '-' + str(idx)
            reg_roi = roi_from_mask(mask, coords_im, mask_idx)
            reg_roi.setName(names[idx])
            # append to list
            registered_rois.append(reg_roi)
         
        coords_im.flush()
         
    # add the cells and lesion to roimanager and paint the atlas
    atlas = IJ.openImage(ATLAS_FILE)
    # IJ.run(atlas, "Reverse", "")
    # atlas.show()
    
    # create a new stack to paint the rois for the lesion
    pa_les = IJ.createImage("lesion_binary", "8-bit black",
                            atlas.getWidth(), atlas.getHeight(), atlas.getNSlices())
    rm = RoiManager()
    for roi in registered_rois:
        r_name = roi.getName()
        if 'lesion-reg_z-' in r_name:
            slice_num = int(r_name.split('-')[-1])
            # atlas.setSliceWithoutUpdate(slice_num)
            roi.setPosition(slice_num)
            rm.addRoi(roi)
            paint_atlas(pa_les, roi, slice_num)
    # save rois and stack
    rm.runCommand("Select All")
    fo_basename = path.join(output_path, mouse_name + '_lesion-analysis_' + res[:-1])
    rm.runCommand("Save", fo_basename + '_lesion-ROIs.zip')
    rm.close()
    IJ.saveAsTiff(pa_les, fo_basename + '_lesion-in-atlas.tif')
    
    # create a new stack to paint the rois for the cells
    pa_cel = IJ.createImage("cells_binary", "8-bit black",
                           atlas.getWidth(), atlas.getHeight(), atlas.getNSlices())
    rm = RoiManager()
    for roi in registered_rois:
        r_name = roi.getName()
        if 'cells-reg_z-' in r_name:
            slice_num = int(r_name.split('-')[-1])
            # atlas.setSliceWithoutUpdate(slice_num)
            roi.setPosition(slice_num)
            rm.addRoi(roi)
            paint_atlas(pa_cel, roi, slice_num)
    # save rois and stack
    rm.runCommand("Select All")
    rm.runCommand("Save", fo_basename + '_cells-ROIs.zip')
    rm.close()
    IJ.saveAsTiff(pa_cel, fo_basename + '_cells-in-atlas.tif')
    
    # interpolate with 3D suite
    pa_cel.show()
    pa_les.show()
    save_interpolated(pa_cel, fo_basename + '_cells-in-atlas-interpolated.tif')
    save_interpolated(pa_les, fo_basename + '_lesion-in-atlas-interpolated.tif')
    
    # close
    pa_cel.close()
    pa_les.close()
    pa_cel.flush()
    pa_les.flush()
    atlas.close()
    atlas.flush()
    
    print('Done')
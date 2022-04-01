# Hernando Martinez April 2022
# This script gets numbers for the lesioned area in each slice
# Specifically, the proportion of cells left in the striatum

from ij import IJ
from ij.plugin.frame import RoiManager
import os
import glob

FILE_ENDING = 'cells-ROIs.zip'
CAUDOPUTAMEN_FILE = r'C:\Users\herny\Desktop\SWC\Data\Anatomy\AllanBrainAtlas_Images\Caudoputamen_25umpx.tif'

# quantify roi
if __name__ in ['__builtin__', '__main__']:
    IJ.run("Close All")
    # get a directory
    input_path = IJ.getDirectory('choose a path containing your processed animals')
    # get a list of the animals analised
    animals_in_folder = os.listdir(input_path)
    # list of lesions stacks paths
    roi_file_list = []
    for folder in animals_in_folder:
        files = glob.glob(os.path.join(input_path, folder, '*' + FILE_ENDING))

        if len(files) > 1:
            print('Something weird in folder {}'.format(folder))

        for file in files:
            print('Found file for animal {}'.format(folder))
            roi_file_list.append(file)

    #Open caudoputamen mask
    cp_imp = IJ.openImage(CAUDOPUTAMEN_FILE)    
    # cp_imp.show()
    # Open file to write
    fout_path = os.path.join(input_path, os.path.basename(__file__.split('.')[0]) + '_output.txt')
    outf = open(fout_path, 'w')
    outf.write(','.join(['mouse_name',
                         'experimental_group',
                         'slide',
                         'slice',
                         '25umpx_atlas_position',
                         'caudoputamen_pixel_number',
                         'intact_cells_pixel_number',
                         'proportion_intact']))

    for n, roifile in enumerate(roi_file_list):
        print('Processing... {} / {}'.format(n + 1, len(roi_file_list)))
        # open roi manager
        rm = RoiManager()
        # load the regions file
        rm.runCommand("Open", roifile)
        # get the number of ROIs in the file
        rois_number = rm.getCount()
        for roi_index in range(rois_number):
            roi = rm.getRoi(roi_index)
            # get name
            roi_name = rm.getName(roi_index)
            name_parts = roi_name.split('_')
            mouse_name = name_parts[0]
            experimental_group = name_parts[1]
            slide = name_parts[2].split('-')[1]
            slicen = name_parts[3].split('-')[1].split('.tif')[0]
            atlas_position = name_parts[-1].split('-')[1]
            # quantify area
            intact_cells_pixel_number = len(roi.getContainedPoints())
            # quantify caudoputamen area of the same slice
            cp_imp.setSlice(int(atlas_position))
            cp_arr = cp_imp.getProcessor().getFloatArray()
            caudoputamen_pixel_number = sum([sum(x) for x in cp_arr])/255
            # calculate proportion
            proportion_intact = float(intact_cells_pixel_number) / caudoputamen_pixel_number
            # write info to text file
            outf.write('\n' + ','.join([mouse_name,
                                        experimental_group,
                                        slide,
                                        slicen,
                                        atlas_position,
                                        str(caudoputamen_pixel_number),
                                        str(intact_cells_pixel_number),
                                        str(proportion_intact)]))
        
        rm.close()
    
    # close caudoputamen file
    cp_imp.flush()
    # close text file
    outf.close()
    
    print('Done')
    
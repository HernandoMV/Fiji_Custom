# Hernando M. Vergara, SWC
# February 2021
# Save_resolution_and_channel_from_czi.py
# Creates 16-bit .tif files for every slice from a czi file from the slide scanner,
# saving one channel, from a defined piramid, at a desired resolution

# This can be used as a complement to CZI_SlideScanner_ROIsubdivider.py

from ij import IJ  #, ImagePlus, ImageStack
from loci.formats import ImageReader
from ij.plugin import ContrastEnhancer
from os import mkdir, path
import sys
sys.path.append("/C:/Users/herny/Documents/GitHub/Fiji_Custom/")
from functions.czi_structure import get_data_structure, get_binning_factor, open_czi_series
from functions.image_manipulation import extractChannel

piramid_to_open = 4
channel_to_save = 4
final_resolution = 10

# Main
if __name__ in ['__builtin__', '__main__']:
    # get the file
    input_path = IJ.getFilePath("Choose a .czi file")
    reader = ImageReader()
    reader.setId(input_path)
    seriesCount = reader.getSeriesCount()
    # slide scanner makes a piramid of X for every ROI you draw
    # resolution is not updated in the metadata so it needs to be calculated manually
    number_of_images, num_of_piramids = get_data_structure(seriesCount)
    print("Number of images is " + str(number_of_images))
    # set names of subimages in the list, waiting to compare to current outputs
    file_core_name = path.basename(input_path).split('.czi')[0]
    possible_slices = [file_core_name + "_slice-" + str(n)
                       for n in range(number_of_images)]

    binFactor = get_binning_factor(reader, num_of_piramids)
    print("Binning factor is " + str(binFactor))

    # create output directory if it doesn't exist
    output_res_path = '000_Slices_for_ARA_registration_' + str(final_resolution) + '_umpx'
    output_path = path.join(path.dirname(path.dirname(input_path)), 'ROIs', output_res_path)
    if path.isdir(output_path):
        print("Output path was already created")
    else:
        mkdir(output_path)
        print("Output path created")

    # for each slice name:
    for sl_name in possible_slices:
        # parse the slice number
        sl_num = int(sl_name.split('-')[-1])
        print("Processing image " + sl_name)
        # open the image
        # get the Xth resolution binned, depending on the number
        # of resolutions. The order is higher to lower.
        series_num = sl_num * num_of_piramids + piramid_to_open
        raw_image = open_czi_series(input_path, series_num)
        # save the resolution (every image has the high-resolution information)
        res_xy_size = raw_image.getCalibration().pixelWidth
        res_units = raw_image.getCalibration().getXUnit()
        # select the requested channel and adjust the intensity
        regist_image = extractChannel(raw_image, channel_to_save, 1)
        # TODO: test if contrast enhancement and background sustraction are needed for registration
        #ContrastEnhancer().stretchHistogram(ch_image, 0.35)
        # IMPLEMENT BACKGROUND SUSTRACTION HERE
        regist_image.setTitle(sl_name)
        #ch_image.show()
        # clean
        raw_image.close()
        raw_image.flush()
        # convert to Xum/px so that it can be aligned to ARA
        reg_im_bin_factor = binFactor / (2 ** (piramid_to_open - 1))
        regres_resolution = reg_im_bin_factor * res_xy_size
        rescale_factor = regres_resolution / final_resolution
        new_width = int(rescale_factor * regist_image.getWidth())
        # self.lr_dapi_reg.getProcessor().scale(rescale_factor, rescale_factor)
        ip = regist_image.getProcessor().resize(new_width)
        regist_image.setProcessor(ip)
        # Add the information to the metadata
        regist_image.getCalibration().pixelWidth = final_resolution
        regist_image.getCalibration().pixelHeight = final_resolution
        regist_image.getCalibration().pixelDepth = 1
        regist_image.getCalibration().setXUnit("micrometer")
        regist_image.getCalibration().setYUnit("micrometer")
        regist_image.getCalibration().setZUnit("micrometer")
        # Save image
        reg_slice_name = path.join(output_path, sl_name)
        IJ.saveAsTiff(regist_image, reg_slice_name)
        regist_image.close()
        regist_image.flush()
    print("Done")
    print("See your images in {}".format(output_path))

# Hernando M. Vergara, SWC
# March 2020
# based on GroupPercentileThresholding.py
# Pipeline to normalize intensities for each channel in each animal, from a group of
# 16-bit images and convert to 8-bit
# This is supposed to be used after CZI_SlideScanner_ROIsubdivider.py

from ij import IJ, ImagePlus, WindowManager
from ij.plugin import FolderOpener, Duplicator, ZProjector
from ij.io import Opener, DirectoryChooser
import sys
import os
import math
from os import path
from ij.process import ImageConverter
import random


def getTifImages(path):
    listTif = []
    listAll = os.listdir(path)
    for f in listAll:
        if '.tif' in f:
            listTif.append(f)
    return listTif


def UniqueMouseIDs(array):
    mouseIds = []
    for i in array:
        mouseIds.append(i.split('_')[0])
    return list(set(mouseIds))


def getMouseFiles(array, mouseID):
    arrToRet = []
    for i in array:
        if mouseID in i:
            arrToRet.append(i)
    return arrToRet


def getNumberOfChannels(MouseIDFiles):
    # returns the number of channels based on the ending of the files (..._channel-1.tif)
    return len(set([x.split('_channel-')[-1] for x in MouseIDFiles]))


def getChannelFiles(MouseIDFiles, channel):
    # returns a selection of a list based no the ending of the files
    return [x for x in MouseIDFiles if x.endswith("-" + str(channel) + ".tif")]


def get_enhance_bounds(chf_fpaths, low_theshold, high_threshold):
    # initialize the pixels array
    pix = []
    # open 100 images max (time consuming)
    if len(chf_fpaths) > 100:
        chf_fpaths = random.sample(chf_fpaths, 100)
    # create a for loop here
    counter = 1
    for image_path in chf_fpaths:
        # open the image
        print "Getting pixels in Image " + image_path
        print str(counter) + " / " + str(len(chf_fpaths))
        imp_orig = Opener().openImage(image_path)
        # get the pixel values
        image_pix = list(imp_orig.getProcessor().getPixels())
        imp_orig.close()
        imp_orig.flush()
        # select randomly 10% of the pixels (maybe memory issues)
        image_pix_sel = random.sample(image_pix, int(len(image_pix) * 0.1))
        pix = pix + image_pix_sel

    # get the percentile values to threshold
    IJ.log('Quantifying pixel values for contrast enhancement...')
    low_pix = percentile(pix, low_theshold)
    high_pix = percentile(pix, high_threshold)

    return low_pix, high_pix


def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]


# Main
if __name__ in ['__builtin__', '__main__']:
    # enhace the images by saturating 0.1% of the pixels (bottom and top)
    low_theshold = 0.1
    high_threshold = 99.9

    IJ.run("Close All")
    In_dir = DirectoryChooser("Select the directory containing your ROI images").getDirectory()
    # Directory to save stuff
    Out_dir = In_dir[:-1] + "--Gce_processed"
    if not os.path.exists(Out_dir):
        os.makedirs(Out_dir)
    else:
        print "Output directory exists already, data might be overwritten"

    # get tif files
    ListTif = getTifImages(In_dir)
    # if it is empty stop
    if len(ListTif) == 0:
        os.rmdir(Out_dir)
        sys.exit('No .tif images found, bye')

    # get unique MouseIDs
    MouseIDs = UniqueMouseIDs(ListTif)

    for MouseID in MouseIDs:
        IJ.log("\nProcessing mouse " + MouseID)
        # get the list of cFos images for a specific mouse
        MouseIDFiles = getMouseFiles(ListTif, MouseID)
        # calculate the number of channels
        number_of_channels_in_mouse = getNumberOfChannels(MouseIDFiles)
        print str(MouseID) + " contains " + str(number_of_channels_in_mouse) + " distinct channels"
        # run the function for each of the channels
        for channel in range(1, (number_of_channels_in_mouse + 1)):
            channel_files = getChannelFiles(MouseIDFiles, channel)
            # get the full path
            chf_fpaths = [path.join(In_dir, x) for x in channel_files]
            # get the minimum and maximum pixel value
            min_pixval, max_pixval = get_enhance_bounds(chf_fpaths, low_theshold, high_threshold)
            IJ.log("Found pixel bounds " + str(min_pixval) + " and " + str(max_pixval) + " for channel " + str(channel))
            counter = 1
            for chfile in chf_fpaths:
                # open file
                ch_img = Opener().openImage(chfile)
                ch_tit = ch_img.getTitle()
                # adjust contrast
                ch_img.getProcessor().setMinAndMax(min_pixval, max_pixval)
                # convert to 8-bit (which also applies the contrast)
                ImageConverter(ch_img).convertToGray8()
                # save
                IJ.saveAsTiff(ch_img, path.join(Out_dir, ch_tit))
                # close and flush
                ch_img.close()
                ch_img.flush()
                print "Image " + str(counter) + " of " + str(len(chf_fpaths)) + " processed"
                counter += 1

        IJ.log('Mouse ' + MouseID + ' processed')

    print "DONE, find your results in " + Out_dir

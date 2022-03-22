# Hernando M. Vergara March 2022

# This scripts gets slices with NeuN staining and finds an ROI for a lesioned area
# the slices should be registered using ABBA

from ij import IJ, ImagePlus
from ij.gui import Plot, Overlay
from ij.plugin.frame import RoiManager
from ij.plugin import ImageCalculator, Selection
from java.awt import Color
import glob
from os import path, makedirs
import sys
sys.path.append(path.abspath(path.dirname(__file__)))
from functions.image_manipulation import extractChannel, create_mask_from_roi   
from functions.image_manipulation import apply_mask_to_image, find_threshold, image_to_roi
from functions.roi_and_ov_manipulation import get_ARA_roi

# ARA areas
STR = 'Caudoputamen'
# FBR = 'fiber tracts'
CTX = 'Isocortex'

# blur value
BLURVAL = 3

# threshold method
THR_METHOD = 'Intermodes'#'RenyiEntropy'#


def add_histogram_to_plot(image_title, base_plot, color):
    base_plot.setColor(color)      
    IJ.selectWindow(image_title)
    im = IJ.getImage()
    pix = list(im.getProcessor().getPixels())
    # remove 0s
    pix = [i for i in pix if i != 0]
    base_plot.addHistogram(pix)
    return pix    


def apply_threshold(image_title, thrvalue, maxval):
    IJ.selectWindow(image_title)
    im = IJ.getImage()
    # thr_image = Duplicator().run(im)
    # thr_image.setTitle()
    # imp = im.getProcessor()
    IJ.setThreshold(im, thrvalue, maxval)
    IJ.run(im, "Create Selection", "")
    # imp.setThreshold(thrvalue, maxval, 0)
    # thr_mask = imp.createMask()
    # thr_mask.outline()
    # return thr_mask
    # thr_image = ImagePlus(image_title+' thresholded', thr_mask)
    # thr_image_pr = thr_image.getProcessor()
    # thr_image_pr.invert()
    # return thr_image

# Main
if __name__ in ['__builtin__', '__main__']:
    IJ.run("Close All")
    # get a directory and find the list of candidate slices
    input_path = IJ.getDirectory('choose a path containing your images')
    # create a new directory where to work
    # find resolution of slices
    res = input_path.split('_')[-1]
    output_path = path.dirname(path.dirname(input_path))
    output_path = path.join(path.dirname(output_path), 'Lesion_quantification_' + res)
    print('Savin in {}'.format(output_path))
    if path.isdir(output_path):
        print("Output path was already created")
    else:
        makedirs(output_path)
        print("Output path created")
    # find candidate slices
    candidate_slices = []
    for file in glob.glob(input_path + '*[0-9].tif'):
        candidate_slices.append(file)

    # check that it has been registered and there are rois
    slices_to_process = []
    for file in candidate_slices:
        rois_file = file + '_ch0.zip'
        coords_file = file + '_ch0_Coords.tif'
        if not (path.exists(rois_file) and path.exists(coords_file)):
            print('Slice {} has not been registered'.format(path.basename(file)))
        else:
            slices_to_process.append(file)

    # open the slice and load a region
    for slice in slices_to_process:
        slice_name = path.basename(slice)
        print('Processing {}'.format(slice_name))
        # open
        im = IJ.openImage(slice)
        # select channel 2
        NeuN_im = extractChannel(im, 2, 1)
        # Convert to 8bit and rename
        # ImageConverter(NeuN_im).convertToGray8()
        NeuN_im.setTitle(slice_name)
        # regions file 
        rois_file = slice + '_ch0.zip'
        # create masks out of rois
        for rn in [STR, CTX]:
            # get roi
            reg_roi = get_ARA_roi(rois_file, rn)
            mask = create_mask_from_roi(reg_roi, rn, NeuN_im)
            # subtract
            mask.show()
            masked_im = apply_mask_to_image(NeuN_im, mask, rn+' masked', BLURVAL)
            masked_im.show()
            mask.close()
            mask.flush()
        
        '''
        # create histogram plot
        my_plot = Plot('Histograms of masked images', 'intensities', 'frequencies')
        # get the histogram of the cortex and add it to the plot
        cortex_hist = add_histogram_to_plot(CTX+' masked', my_plot, 'black')
        # for the fibers
        fibers_hist = add_histogram_to_plot(FBR+' masked', my_plot, 'red')
        # for the striatum
        str_hist = add_histogram_to_plot(STR+' masked', my_plot, 'blue')
        # show histogram
        my_plot.show()
        '''

        # calculate a threshold value based on the cortex
        thr_value, max_val = find_threshold(CTX+' masked', THR_METHOD)
        print('Threshold value for {} is {}'.format(slice_name, thr_value))

        # apply it to the striatum
        # thr_str = apply_threshold(STR+' masked', thr_value, max_val)
        apply_threshold(STR+' masked', thr_value, max_val)
        # get the anti-lesion roi
        rm = RoiManager()
        IJ.selectWindow(STR+ ' masked')
        rm.runCommand("add")
        cells_roi = rm.getRoi(0)
        cells_roi.setName(slice_name+'-cells')
        rm.close()
        # rm.runCommand("Save", slice+'_lesionROI.roi')
        # thr_str.show()

        # rm = RoiManager()
        # rm.addRoi(thr_str)

        # # convert it to a ROI
        # lesion_roi = image_to_roi(thr_str)

        # # show in original image
        # # ov = Overlay()
        # # lesion_roi.setStrokeColor(Color.GREEN)
        # # lesion_roi.setLineWidth(1)
        # # ov.add(lesion_roi)
        # # NeuN_im.setOverlay(ov)
        # # NeuN_im.updateAndDraw()
        # # fp = NeuN_im.getProcessor()
        # # fp.setRoi(lesion_roi)
        # # fp.fill(lesion_roi.getMask())

        # Close images
        for rn in [STR, CTX]:
            IJ.selectWindow(rn + ' masked')
            im = IJ.getImage()
            im.close()
            im.flush()

        # find the lesion roi
        # cp_roi = get_ARA_roi(input_file=rois_file, region_name=STR)
        reg_roi = get_ARA_roi(rois_file, STR)
        mask = create_mask_from_roi(reg_roi, STR, NeuN_im)
        mask.show()
        # subtract the cells_roi
        cells_mask = create_mask_from_roi(cells_roi, 'cells', NeuN_im)
        cells_mask.show()
        ImageCalculator().run(mask, cells_mask, 'subtract')
        IJ.setThreshold(mask, 1, 65535)
        IJ.run(mask, "Create Selection", "")
        rm = RoiManager()
        IJ.selectWindow(STR)
        rm.runCommand("add")
        lesion_roi = rm.getRoi(0)
        lesion_roi.setName(slice_name+'-lesion')
        rm.close()
        mask.close()
        mask.flush()
        cells_mask.close()
        cells_mask.flush()

        # overlay on main image and save
        NeuN_im.show()
        IJ.run(NeuN_im, 'Fire', '')
        nimp = NeuN_im.getProcessor()
        nimp.setRoi(cells_roi)
        ov = Overlay()
        cells_roi.setStrokeColor(Color.GREEN)
        cells_roi.setLineWidth(1)
        ov.add(cells_roi)
        lesion_roi.setStrokeColor(Color.RED)
        ov.add(lesion_roi)
        NeuN_im.setOverlay(ov)
        NeuN_im.updateAndDraw()
        imp2 = NeuN_im.flatten()
        imp2.show()
        o_file_name = path.join(output_path, slice_name.split('.tif')[0]+'_lesionROI')
        IJ.saveAsTiff(imp2, o_file_name + '.tif')
        NeuN_im.close()
        NeuN_im.flush()
        imp2.close()
        imp2.flush()

        rm = RoiManager()
        rm.addRoi(cells_roi)
        rm.addRoi(lesion_roi)
        rm.runCommand("Select All")
        rm.runCommand("Save", o_file_name + '.zip')
        rm.close()



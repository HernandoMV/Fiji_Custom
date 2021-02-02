# Hernando M. Vergara, SWC
# Feb 2021
# czi_structure.py
# functions to deal with .czi slide scanner files

#import sys
from loci.plugins.in import ImporterOptions
from loci.plugins import BF
from loci.common import Region


def get_data_structure(seriesCount):
    num_of_real_images = seriesCount - 2
    if num_of_real_images % 6 == 0:
        num_of_piramids = 6
    if num_of_real_images % 7 == 0:
        num_of_piramids = 7
    if num_of_real_images % 8 == 0:
        num_of_piramids = 8
    # else:
        # sys.exit('Number of images is weird, check manually and change the code')
    number_of_images = int(num_of_real_images / num_of_piramids)

    return [number_of_images, num_of_piramids]


def get_binning_factor(r, num_of_piramids):
    r.setSeries(0)
    high_res = r.getSizeX()
    r.setSeries(num_of_piramids - 1)
    low_res = r.getSizeX()

    return high_res / low_res


def open_czi_series(file_name, series_number, rect=False):
    # see https://downloads.openmicroscopy.org/bio-formats/5.5.1/api/loci/plugins/in/ImporterOptions.html
    options = ImporterOptions()
    options.setId(file_name)
    options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
    # select image to open
    options.setOpenAllSeries(False)
    options.setAutoscale(False)
    options.setSeriesOn(series_number, True)
    # default is not to crop
    options.setCrop(False)
    if rect:  # crop if asked for
        options.setCrop(True)
        options.setCropRegion(series_number, Region(rect[0], rect[1], rect[2], rect[3]))
    imps = BF.openImagePlus(options)

    return imps[0]

from loci.common import Region
from loci.plugins.in import ImporterOptions
from loci.plugins import BF
from loci.formats import ImageReader

#path = IJ.getFilePath("Choose a File")
path = "C:\Users\herny\Desktop\SWC\Data\Microscopy_Data\Histology_of_tail_lesions\DRD1KO\cont-01-3.czi"


def open_czi_series(file_name, series_number, rect=False):
	# see https://downloads.openmicroscopy.org/bio-formats/5.5.1/api/loci/plugins/in/ImporterOptions.html
	options = ImporterOptions()
	options.setId(file_name)
	options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
	# select image to open
	options.setOpenAllSeries(False)
	options.setAutoscale(False)
	options.setSeriesOn(series_number, True)
	if rect: #crop if asked for
		options.setCrop(True)
		options.setCropRegion(series_number, Region(rect[0], rect[1], rect[2], rect[3]))
	imps = BF.openImagePlus(options)
	return imps[0]

def get_binning_factor(r):
	r.setSeries(0)
	high_res = r.getSizeX()
	r.setSeries(6)
	low_res = r.getSizeX()
	return high_res/low_res

# get the info about the number of images in the file

reader = ImageReader()
reader.setId(path)
seriesCount = reader.getSeriesCount()
# slide scanner makes a piramid of 7 for every ROI you draw
# resolution is not updated in the metadata so it needs to be calculated manually
number_of_images = seriesCount/7
print "Number of images is " + str(number_of_images)
binFactor = get_binning_factor(reader)
print binFactor

# get an image
myimage = open_czi_series(path, 6, rect=[1,5,400,400])
myimage.show()


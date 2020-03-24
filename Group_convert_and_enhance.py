# Hernando M. Vergara, SWC
# March 2020
# based on GroupPercentileThresholding.py
# Pipeline to normalize intensities for each channel in each animal, from a group of
# 16-bit images and convert to 8-bit
# This is supposed to be used after CZI_SlideScanner_ROIsubdivider 

from ij import IJ, ImagePlus, WindowManager
from ij.plugin import FolderOpener, Duplicator, ZProjector
from ij.plugin.filter import GaussianBlur
from ij.io import Opener, DirectoryChooser
import sys
import os
import math

def getCfosImages(path):
	listCfos = []
	listAll = os.listdir(path)
	for f in listAll:
		if 'cFos.tif' in f:
			listCfos.append(f)
	return listCfos 

def UniqueMouseIDs(array):
	mouseIds = []
	for i in array:
		mouseIds.append(i.split('_')[0])
	return list(set(mouseIds))

def getMouseCfos(array, mouseID):
	arrToRet = []
	for i in array:
		if mouseID in i:
			arrToRet.append(i)
	return arrToRet

def FindThreholds(mainpath, listOfImages, quantArray):
	#initialize the pixels array
	pix = []
	#create a for loop here
	for image in listOfImages:
		#open the image
		IJ.log('Getting pixels in Image ' + image)
		imp_orig = Opener().openImage(mainpath + image)
		imp_GB = blurImage(imp_orig)
		imp_orig.close()
		imp_GB.hide()
		#get the pixel values
		pix = getPixelValues(imp_GB, pix)
		imp_GB.close()
		
	#get the percentile values to threshold
	IJ.log('Quantifying thresholds...')
	percs = []
	for q in quantArray:
		percs.append(percentile(pix, q))	
	return percs
	
def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100))-1]

def getPixelValues(imp, vector):
	#appends the pixel values of an image to a given vector
	for k in range(imp.getStackSize()):
		ip = imp.getProcessor()
		for j in range(ip.getHeight()):
			for i in range(ip.getWidth()):
				vector.append(ip.getPixel(i, j))
	return vector

def blurImage(ip):
	#duplicate
	imp_dup = Duplicator().run(ip)
	#blur it
	imp_dup.show()
	IJ.run(imp_dup, "Gaussian Blur...", "sigma=1");
	imp_GB = IJ.getImage()
	return(imp_GB)


#Main 
if __name__ in ['__builtin__', '__main__']:
	IJ.run("Close All")
	In_dir = DirectoryChooser("Select the directory containing your cropped images").getDirectory()
	#Directory to save stuff
	Out_dir = In_dir[:-1] + "--GPTprocessed/"
	if not os.path.exists(Out_dir):
		os.makedirs(Out_dir)
	else:
		print "Output directory exists already, data might be overwritten"
		
	#crop images ?

	#get c-Fos
	ListCfos = getCfosImages(In_dir)
	#if it is empty stop
	if len(ListCfos)==0:
		os.rmdir(Out_dir)
		sys.exit('No c-Fos images found')
		
	
	#get unique MouseIDs
	MouseIDs = UniqueMouseIDs(ListCfos)

	for MouseID in MouseIDs:
		IJ.log("\nProcessing mouse " + MouseID)
		#get the list of cFos images for a specific mouse
		MouseIDcFos = getMouseCfos(ListCfos, MouseID)
		#find the threshold values using the quantiles
		percentiles = [98.5, 99.5, 99.9]
		thresholds = FindThreholds(In_dir, MouseIDcFos, percentiles)
		IJ.log('Thresholds for percentiles ' + str(percentiles) + ' selected to ' + str(thresholds))
		#threshold and save images for each threshold value
		for i, threshold in enumerate(thresholds):
			# create directory
			Perc_Out_dir = Out_dir + "percentile_" + str(percentiles[i]) + "/"
			if not os.path.exists(Perc_Out_dir):
				os.makedirs(Perc_Out_dir)
			IJ.log('Processing ' + MouseID + ' for percentile ' + str(percentiles[i]))
			for image in MouseIDcFos:
				#open image
				imp_orig = Opener().openImage(In_dir + image)
				#gaussian blur
				imp_GB = blurImage(imp_orig)
				imp_orig.close()
				#threshold
				imp_GB.getProcessor().threshold(threshold)
				#save
				newname = image.split('.')[0] + '_GPT_' + str(percentiles[i]) + '.tif'
				IJ.saveAsTiff(imp_GB, Perc_Out_dir + newname)
				imp_GB.close()
				
		IJ.log('Mouse ' + MouseID + ' processed')	

	
	print "DONE, find your results in " + Out_dir

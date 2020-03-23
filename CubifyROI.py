# Hernando M. Vergara
# March 2020. Coronavirus quarantine :)
# CubifyROI.py takes as input a folder containing images in trios (channels) with names 'DAPI', 'D2', and 'D1'
# It subdivides the drawn ROIs into square rois within that ROI, and saves them independently

from javax.swing import JFrame, JButton, JPanel, JTextField, JSlider, JCheckBox, JList, JLabel, BorderFactory, JScrollPane, SwingConstants, DefaultListModel
from java.awt import GridLayout, Dimension, GraphicsEnvironment, BorderLayout, Label, Color, Font
from ij.io import OpenDialog, Opener, DirectoryChooser, FileSaver
from ij import ImagePlus, IJ, WindowManager, ImageStack
from ij.plugin import WindowOrganizer, ZProjector, ImageCalculator, Macro_Runner, FolderOpener, Duplicator
from os import listdir, path, mkdir, remove
from ij.plugin.frame import SyncWindows, ThresholdAdjuster
from ij.process import ImageProcessor
from ij.gui import WaitForUserDialog, Roi, TextRoi, PolygonRoi, Overlay


class gui(JFrame):
	def __init__(self): # constructor 
		#origing of coordinates
		self.coordx = 10
		self.coordy = 10
	
		#inintialize values
		self.Canvas = None
		
		#create panel (what is inside the GUI)
		self.panel = self.getContentPane()
		self.panel.setLayout(GridLayout(9,2))
		self.setTitle('Subdividing ROIs')

		#define buttons here:
		self.Dapi_files = DefaultListModel()
		mylist = JList(self.Dapi_files, valueChanged=self.open_dapi_image)
		#mylist.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		mylist.setLayoutOrientation(JList.VERTICAL)
		mylist.setVisibleRowCount(-1)
		listScroller1 = JScrollPane(mylist)
		listScroller1.setPreferredSize(Dimension(300, 80))

		self.output_files = DefaultListModel()
		mylist2 = JList(self.output_files)
		#mylist.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		mylist2.setLayoutOrientation(JList.VERTICAL)
		mylist2.setVisibleRowCount(-1)
		listScroller2 = JScrollPane(mylist2)
		listScroller2.setPreferredSize(Dimension(300, 80))
		
		quitButton = JButton("Quit", actionPerformed = self.quit)
		selectInputFolderButton = JButton("Select Input", actionPerformed = self.select_input)
		cubifyROIButton = JButton("Cubify ROI", actionPerformed = self.cubify_ROI)
		saveButton = JButton("Save ROIs", actionPerformed = self.save)
		summsaveButton = JButton("Save Summary", actionPerformed = self.save_summary)
		
		self.textfield1 = JTextField('500')
		
		#add buttons here
		self.panel.add(listScroller1)
		self.panel.add(listScroller2)
		self.panel.add(selectInputFolderButton)
		self.panel.add(Label("Adjust the size of the ROIs"))
		self.panel.add(self.textfield1)
		self.panel.add(cubifyROIButton)
		self.panel.add(saveButton)
		self.panel.add(summsaveButton)
		self.panel.add(quitButton)
		
		#self.panel.add(saveButton)
		#self.panel.add(Zslider)

       	#other stuff to improve the look
		self.pack() # packs the frame
		self.setVisible(True) # shows the JFrame
		self.setLocation(self.coordx,self.coordy)


	#define functions for the buttons:
	       
	def quit(self, event): #quit the gui
		self.dispose()
		IJ.run("Close All")

	def select_input(self, event):
		self.input_path = IJ.getDirectory("Select Directory containing your data")

		# get the files in that directory
		self.input_files = listdir(self.input_path)
		self.input_dapi = [s for s in self.input_files if "DAPI.tif" in s]
		self.core_names = get_core_names(self.input_dapi)
		
		# create output directory
		self.output_path = path.join(path.dirname(path.dirname(self.input_path)), "Cubified_ROIs")
		if path.isdir(self.output_path):
			print "Output path already created"
		else:
			mkdir(self.output_path)
			print "Output path created"
		# get the processed data
		self.processed_files = listdir(self.output_path)
		self.out_core_names = get_core_names(get_core_names(self.processed_files)) # needs the channel and roi to be removed

		# populate the lists
		for f in set(self.core_names):
			if f not in set(self.out_core_names): # skip if processed
				self.Dapi_files.addElement(f)
		for f in set(self.out_core_names): # a set so that only unique ones are shown
			self.output_files.addElement(f)
	
	def open_dapi_image(self, e):
		sender = e.getSource()
		IJ.run("Close All")
		if not e.getValueIsAdjusting():
			self.name = sender.getSelectedValue()
			print self.name
			dapi_filename = path.join(self.input_path, self.name + '_DAPI.tif')
			#print dapi_filename
			if not path.exists(dapi_filename):
				print "I don't find the DAPI file, which is weird as I just found it before"
			else: 
				#open stack and make the reslice
				self.dapi_image = ImagePlus(dapi_filename) #read the image
				# duplicate image to play with that one, and do the real processing in the background
				self.imp_main = Duplicator().run(self.dapi_image)
				self.imp_main.setTitle(self.name)
				self.imp_main.show() #show image on the left
				#self.original_image.getWindow().setLocation(self.coordx-self.original_image.getWindow().getWidth()-10,self.coordy-10) #reposition image

	def cubify_ROI(self, e):
		self.L = int(self.textfield1.text)
		# get info
		tit = self.imp_main.getTitle()
		self.roi = self.imp_main.getRoi()
	
		# get corners
		corners = get_corners(self.roi, self.L)
		self.corners_cleaned = clean_corners(corners, self.roi, self.L)		
		print 'found corners'
		# get the overlay
		self.ov = overlay_corners(self.corners_cleaned, self.L)
		self.ov = overlay_roi(self.roi, self.ov)
		# write roi name
		self.ov = write_roi_numbers(self.ov, self.corners_cleaned, self.L)
		# overlay
		self.imp_main.setOverlay(self.ov)
		self.imp_main.updateAndDraw()

	def save(self, e):
		# open the other channels
		d1_filename = path.join(self.input_path, self.name + '_D1.tif')
		d2_filename = path.join(self.input_path, self.name + '_D2.tif')
		self.d1_image = ImagePlus(d1_filename) #read the image
		print "d1 image opened"
		self.d2_image = ImagePlus(d2_filename) #read the image
		print "d2 image opened"
		for image in [self.dapi_image, self.d1_image, self.d2_image]:
			print "saving rois for image " + image.getTitle()
			save_rois(image, self.corners_cleaned, self.L, self.output_path)
		print "ROIs saved"

	def save_summary(self, e):
		IJ.selectWindow(self.name)
		IJ.run("Flatten")
		imp = IJ.getImage()
		# downsample
		# scale ENLARGING or SHRINKING the canvas dimensions  
		scale_factor = .2
		new_width = str(int(imp.getWidth() * scale_factor))
		new_height = str(int(imp.getHeight() * scale_factor))
		IJ.selectWindow(self.name + "-1")
		str_to_scale = "x=" + str(scale_factor) + " y=" + str(scale_factor) + " width=" + new_width + " height=" + new_height + " interpolation=Bilinear average create"
		IJ.run("Scale...", str_to_scale)
		# save
		imp2 = IJ.getImage()
		#IJ.saveAs("Tiff", path.join(OUTDIR, self.name + "_summaryOfROIs"))
		IJ.saveAsTiff(imp2, path.join(self.output_path, self.name + "_summaryOfROIs.tif"))
		print "summary image saved"
	
# other functions
def get_core_names(dapi_names):
	core_names = []
	for name in dapi_names:
		core_names.append('_'.join(name.split('_')[0:-1]))
	return core_names

def get_corners( roi, L ):
	# get the points inside roi
	poly = roi.getContainedFloatPoints()
	xs = poly.xpoints
	ys = poly.ypoints
	# create an empty set to hold the corners
	corners = set()
	for x,y in zip(xs,ys):
		# add the modulo of the size to set
		# need to be tuple, lists can't be adde to a set
		xc = x-x%L
		yc = y-y%L
		corners.add( (xc, yc))
	return corners

def overlay_corners(corners, L):
	ov = Overlay()
	for [x,y] in corners:
		rect = Roi(x,y,L,L)
		rect.setStrokeColor(Color.RED)
		rect.setLineWidth(40)
		ov.add(rect)
	return ov

def overlay_roi(roi, ov):
	roi.setStrokeColor(Color.GREEN)
	roi.setLineWidth(40)
	ov.add(roi)
	return ov
	
def clean_corners(corners, roi, L):
	# get the points inside roi
	poly = roi.getContainedPoints()
	#print(poly)
	xs = [int(p.getX()) for p in poly]
	#print(xs)
	ys = [int(p.getY()) for p in poly]
	points = zip(xs,ys)
	corners_cleaned = set()
	for c in corners:
		if c in points: # if the corner is inside
			if (c[0]+L, c[1]+L) in points: # if the opposite corner is inside
				if (c[0]+L, c[1]) in points:
					if (c[0], c[1]+L) in points:
						corners_cleaned.add(c)
	return corners_cleaned

def get_centers(corners, L):
	centers = set()
	for [x,y] in corners:
		centers.add( (int(x+L/2), int(y+L/2)) )
	return centers
	
def write_roi_numbers(ov, corners, L):
	roiID = 1
	for [x,y] in corners:
		text = TextRoi(x,y,L,L,str(roiID),Font("Arial", Font.PLAIN, 400))
		text.setJustification(1)
		text.setColor(Color.RED)	
		ov.add(text)
		roiID += 1
	return ov

def save_rois(imp, corners_cleaned, L, OUTDIR):
	# parse title
	tit = imp.getTitle()
	core = '_'.join(tit.split('_')[0:-1])
	ending = tit.split('_')[-1]
	# save rois
	roi_ID = 1
	for [x,y] in corners_cleaned:
		rect = Roi(x,y,L,L)
		imp.setRoi(rect)
		imp2 = imp.crop()
		# save
		IJ.saveAsTiff(imp2, path.join(OUTDIR, core + "_ROI-" + str(roi_ID) + "_" + ending))
		roi_ID += 1
	

if( __name__ == '__builtin__'):
	gui()
	#WaitForUserDialog('Stop').show()

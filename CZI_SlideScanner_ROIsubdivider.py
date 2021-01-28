# Hernando M. Vergara
# March 2020. Coronavirus quarantine :)
# CZI_SlideScanner_ROIsubdivider.py takes as input a .czi file from the slide scanner
# The input files should contain
# ...
# It subdivides the drawn ROIs into square rois within that ROI, and saves them independently

# This is optimized for working with the low and high resolution images generated when acquiring
# with the 40x objective


from loci.common import Region
from loci.plugins.in import ImporterOptions
from loci.plugins import BF
from loci.formats import ImageReader
from javax.swing import JFrame, JButton, JPanel, JTextField, JSlider, JCheckBox, JList, JLabel, \
    BorderFactory, JScrollPane, SwingConstants, DefaultListModel
from java.awt import GridLayout, Dimension, GraphicsEnvironment, BorderLayout, Label, Color, Font
from ij.io import OpenDialog, Opener, DirectoryChooser, FileSaver, RoiEncoder
from ij import ImagePlus, IJ, WindowManager, ImageStack, CompositeImage
from ij.plugin import WindowOrganizer, ZProjector, ImageCalculator, Macro_Runner, FolderOpener, \
    Duplicator, ContrastEnhancer
from os import listdir, path, mkdir, remove
from ij.plugin.frame import SyncWindows, ThresholdAdjuster
from ij.process import ImageProcessor, ImageConverter
from ij.gui import WaitForUserDialog, Roi, TextRoi, PolygonRoi, Overlay
import sys


class gui(JFrame):
    def __init__(self):  # constructor
        # origing of coordinates
        self.coordx = 10
        self.coordy = 10

        # inintialize values
        self.Canvas = None
        self.default_naming = 'MouseID_ExperimentalGroup_slide-X'

        # create panel (what is inside the GUI)
        self.panel = self.getContentPane()
        self.panel.setLayout(GridLayout(8, 2))
        self.setTitle('Subdividing ROIs')

        # define buttons here:
        self.subimage_number = DefaultListModel()
        mylist = JList(self.subimage_number, valueChanged=self.open_lowres_image)
        # mylist.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        mylist.setLayoutOrientation(JList.VERTICAL)
        mylist.setVisibleRowCount(1)
        listScroller1 = JScrollPane(mylist)
        listScroller1.setPreferredSize(Dimension(200, 90))

        quitButton = JButton("Quit", actionPerformed=self.quit)
        selectInputFolderButton = JButton("Select Input", actionPerformed=self.select_input)
        cubifyROIButton = JButton("Cubify ROI", actionPerformed=self.cubify_ROI)
        saveButton = JButton("Save ROIs", actionPerformed=self.save_ROIs)

        self.textfield1 = JTextField('18')
        self.textfield2 = JTextField(self.default_naming)
        self.textfield3 = JTextField('R-Tail')
        self.textfield4 = JTextField('2, 4, 22.619')
        self.textfield5 = JTextField('2')

        # add buttons here
        self.panel.add(Label("Name your image, or use filename"))
        self.panel.add(self.textfield2)
        self.panel.add(selectInputFolderButton)
        self.panel.add(listScroller1)
        self.panel.add(Label("Adjust the size of the squared ROIs"))
        self.panel.add(self.textfield1)
        self.panel.add(Label("give a name of your hand-drawn ROI"))
        self.panel.add(self.textfield3)
        self.panel.add(Label("For ARA: piram, ch, res"))
        # piramid number (low to high), channel number, final resolution (um/px)"))
        self.panel.add(self.textfield4)
        self.panel.add(Label("Piramid to check (0:none; 1:highest)"))
        self.panel.add(self.textfield5)
        self.panel.add(cubifyROIButton)
        self.panel.add(saveButton)
        self.panel.add(quitButton)

        # other stuff to improve the look
        self.pack()  # packs the frame
        self.setVisible(True)  # shows the JFrame
        self.setLocation(self.coordx, self.coordy)

    # define functions for the buttons:
    def quit(self, event):  # quit the gui
        self.dispose()
        IJ.run("Close All")

    def select_input(self, event):
        # get the info about the number of images in the file
        self.input_path = IJ.getFilePath("Choose a File")
        # if default naming is not changed use file name
        if self.textfield2.text == self.default_naming:
            self.file_core_name = path.basename(self.input_path).split('.czi')[0]
        else:
            self.file_core_name = self.textfield2.text
        # put that name in the text field
        self.panel.getComponents()[1].setText(self.file_core_name)

        reader = ImageReader()
        reader.setId(self.input_path)
        seriesCount = reader.getSeriesCount()
        # slide scanner makes a piramid of X for every ROI you draw
        # resolution is not updated in the metadata so it needs to be calculated manually
        number_of_images, self.num_of_piramids = get_data_structure(seriesCount)
        print("Number of images is " + str(number_of_images))
        # set names of subimages in the list, waiting to compare to current outputs
        self.possible_slices = [self.file_core_name + "_slice-" + str(n)
                                for n in range(number_of_images)]

        self.binFactor = get_binning_factor(reader, self.num_of_piramids)
        print("Binning factor is " + str(self.binFactor))

        # create output directory if it doesn't exist
        self.output_path = path.join(path.dirname(path.dirname(self.input_path)), "ROIs")
        if path.isdir(self.output_path):
            print("Output path was already created")
        else:
            mkdir(self.output_path)
            print("Output path created")

        # update_lists depending on whether something has been processed already
        self.update_list()

    def update_list(self):
        # remove stuff from lists:
        # TODO
        # populate the list
        for f in set(self.possible_slices):
            self.subimage_number.addElement(f)

    def open_lowres_image(self, e):
        sender = e.getSource()
        IJ.run("Close All")
        if not e.getValueIsAdjusting():
            self.name = sender.getSelectedValue()
            print(self.name)
            # parse the slice number
            self.sl_num = int(self.name.split('-')[-1])
            print("Opening slice " + str(self.sl_num))

            if not path.exists(self.input_path):
                print("I don't find the file, which is weird as I just found it before")
            else:
                # get the Xth resolution binned, depending on the number
                # of resolutions. The order is higher to lower.
                series_num = self.sl_num * self.num_of_piramids + (self.num_of_piramids - 1)
                self.low_res_image = open_czi_series(self.input_path, series_num)  # read the image
                # save the resolution (every image has the high-resolution information)
                self.res_xy_size = self.low_res_image.getCalibration().pixelWidth
                self.res_units = self.low_res_image.getCalibration().getXUnit()
                # play with that one, and do the real processing in the background
                # select the DAPI channel and adjust the intensity
                self.lr_dapi = extractChannel(self.low_res_image, 1, 1)
                ContrastEnhancer().stretchHistogram(self.lr_dapi, 0.35)
                self.lr_dapi.setTitle(self.name)
                self.lr_dapi.show()
                # reposition image
                self.lr_dapi.getWindow().setLocation(420, 10)
                self.lr_dapi.updateAndDraw()

                # clean
                self.low_res_image.close()
                self.low_res_image.flush()

    def cubify_ROI(self, e):
        self.manualROI_name = self.name + "_manualROI-" + self.textfield3.text

        # warn the user if that ROI exists already in the processed data
        self.processed_files = listdir(self.output_path)
        self.out_core_names = get_core_names(self.processed_files, self.file_core_name)
        if self.manualROI_name in self.out_core_names:
            print("##################                       ##################")
            print("CAREFUL!!!! This ROI already exists in your processed data:")
            print("##################                       ##################")

        print(self.manualROI_name)

        # set square roi size
        self.L = int(self.textfield1.text)
        # get info
        tit = self.lr_dapi.getTitle()
        self.roi = self.lr_dapi.getRoi()

        # get corners
        corners = get_corners(self.roi, self.L)
        self.corners_cleaned = clean_corners(corners, self.roi, self.L)
        # get the overlay
        self.ov = overlay_corners(self.corners_cleaned, self.L)
        self.ov = overlay_roi(self.roi, self.ov)
        # write roi name
        self.ov = write_roi_numbers(self.ov, self.corners_cleaned, self.L)
        # overlay
        self.lr_dapi.setOverlay(self.ov)
        self.lr_dapi.updateAndDraw()

        # open the Xth highest resolution one to see if it is in focus
        if int(self.textfield5.text) != 0:
            pir_for_focus = int(self.textfield5.text)
            bf_corr = self.binFactor / (2 ** (pir_for_focus - 1))
            min_x = int(min([x[0] for x in self.corners_cleaned]) * bf_corr)
            min_y = int(min([x[1] for x in self.corners_cleaned]) * bf_corr)
            max_x = int((max([x[0] for x in self.corners_cleaned]) + self.L) * bf_corr)
            max_y = int((max([x[1] for x in self.corners_cleaned]) + self.L) * bf_corr)
            series_num = self.sl_num * self.num_of_piramids + pir_for_focus - 1
            self.med_res_image = open_czi_series(
                self.input_path, series_num,
                rect=[min_x, min_y, max_x - min_x, max_y - min_y])  # read the image
            # play with that one, and do the real processing in the background
            self.med_res_image.show()
            self.med_res_image.setDisplayMode(IJ.COMPOSITE)
            color_order = ['Grays', 'Green', 'Red', 'Cyan']
            for c in range(self.med_res_image.getNChannels()):
                self.med_res_image.setC(c + 1)
                IJ.run(color_order[c])
                ContrastEnhancer().stretchHistogram(self.med_res_image, 0.35)
                self.med_res_image.updateAndDraw()
            comp = CompositeImage(self.low_res_image, CompositeImage.COLOR)
            comp.show()
            IJ.Stack.setDisplayMode("composite")
            # IJ.run("RGB")
            # clean
            self.med_res_image.close()
            self.med_res_image.flush()

    def save_ROIs(self, e):
        # save the low resolution image for registration
        self.save_registration_image()

        print('Saving ROIs')
        # add a counter for the ROI name
        roiID = 1

        # create a file to save the ROI coordinates
        # create output directory if it doesn't exist
        self.roi_output_path = path.join(self.output_path, "000_manualROIs_info")
        if path.isdir(self.roi_output_path):
            print("Output path for ROIs information was already created")
        else:
            mkdir(self.roi_output_path)
            print("Output path for ROIs created")
        roi_points_file_path = path.join(self.roi_output_path, self.manualROI_name +
                                         "_roi_positions.txt")
        with open(roi_points_file_path, "w") as roi_points_file:
            roi_points_file.write("{}, {}, {}, {}, {}, {}".
                                  format("roiID", "high_res_x_pos",
                                         "high_res_y_pos", "registration_image_pixel_size",
                                         "high_res_pixel_size", "units"))

        # for each roi
        for [x, y] in self.corners_cleaned:
            print('   -> processing square ROI number ' + str(roiID))
            # tranlate coordinates to high resolution
            xt = int(x * self.binFactor)
            yt = int(y * self.binFactor)
            Lt = int(self.L * self.binFactor)
            # save the corner coordinates of the ROI in a file
            with open(roi_points_file_path, "a") as roi_points_file:
                roi_points_file.write("\n{}, {}, {}, {}, {}, {}".
                                      format(roiID, xt, yt, self.reg_final_res,
                                             self.res_xy_size, self.res_units))

            # open the high resolution image on that roi
            series_num = self.sl_num * self.num_of_piramids
            hr_imp = open_czi_series(self.input_path, series_num, rect=[xt, yt, Lt, Lt])
            # hr_imp.show()
            # name of this ROI
            Roi_name = self.manualROI_name + "_squareROI-" + str(roiID)
            # for each of the channels
            for c in range(1, (hr_imp.getNChannels() + 1)):
                # get the channel
                channel = extractChannel(hr_imp, c, 1)
                # save with coherent name
                IJ.saveAsTiff(channel, path.join(self.output_path, Roi_name + "_channel-" + str(c)))
                # close and flush memory
                channel.close()
                channel.flush()
            # increase counter
            roiID += 1
            # close and flush memory
            hr_imp.close()
            hr_imp.flush()
        print('ROIs saved, saving summary figure')

        # save summary
        # create output directory if it doesn't exist
        self.summary_output_path = path.join(self.output_path, "000_Summary_of_ROIs")
        if path.isdir(self.summary_output_path):
            print("Output path for summary was already created")
        else:
            mkdir(self.summary_output_path)
            print("Output path for summary created")
        IJ.selectWindow(self.name)
        IJ.run("Flatten")
        imp = IJ.getImage()
        IJ.saveAsTiff(imp, path.join(
            self.summary_output_path,
            self.manualROI_name + "_summaryImage"))
        print("summary image saved")
        IJ.run("Close All")

        # save manual ROI
        RoiEncoder.save(self.roi, path.join(self.roi_output_path, self.manualROI_name))
        print("roi information saved, closing images and finishing")
        IJ.run("Close All")

    def save_registration_image(self):
        # TODO: it might be needed to remove the background. Test registration first

        self.forreg_output_path = path.join(self.output_path, "000_Slices_for_ARA_registration")

        if path.isdir(self.forreg_output_path):
            print("Output path for low resolution slices was already created")
        else:
            mkdir(self.forreg_output_path)
            print("Output path for low resolution slices created")

        # check that this slice has not been saved before
        reg_slice_name = path.join(self.forreg_output_path, self.name)
        if path.isfile(reg_slice_name):
            print("Registration slice already exists")
        else:
            # save otherwise
            reg_text_info = self.textfield4.text.split(',')
            reg_pir_num = int(reg_text_info[0])
            reg_channel = int(reg_text_info[1])
            self.reg_final_res = float(reg_text_info[2])
            print("Saving for registration channel {} at {} um/px".format(reg_channel, self.reg_final_res))
            # get the Xth resolution image and Xth channel for saving it for registration
            series_num = self.sl_num * self.num_of_piramids + (self.num_of_piramids - reg_pir_num)
            self.raw_reg_image = open_czi_series(self.input_path, series_num)  # read the image
            self.regist_image = extractChannel(self.raw_reg_image, reg_channel, 1)
            ContrastEnhancer().stretchHistogram(self.regist_image, 0.35)
            # self.regist_image.show()

            self.regist_image.getProcessor().resetRoi()
            # reset min and max automatically
            # convert to 8-bit (which also applies the contrast)
            # ImageConverter(self.regist_image).convertToGray8()
            # convert to Xum/px so that it can be aligned to ARA
            reg_im_bin_factor = self.binFactor / (2 ** (reg_pir_num - 1))
            regres_resolution = reg_im_bin_factor * self.res_xy_size
            rescale_factor = regres_resolution / self.reg_final_res
            new_width = int(rescale_factor * self.regist_image.getWidth())
            # self.lr_dapi_reg.getProcessor().scale(rescale_factor, rescale_factor)
            ip = self.regist_image.getProcessor().resize(new_width)
            self.regist_image.setProcessor(ip)
            # Add the information to the metadata
            self.regist_image.getCalibration().pixelWidth = self.reg_final_res
            self.regist_image.getCalibration().pixelHeight = self.reg_final_res
            self.regist_image.getCalibration().pixelDepth = 1
            self.regist_image.getCalibration().setXUnit("micrometer")
            self.regist_image.getCalibration().setYUnit("micrometer")
            self.regist_image.getCalibration().setZUnit("micrometer")
            # self.lr_dapi_reg.getProcessor().resetRoi()
            IJ.saveAsTiff(self.regist_image, reg_slice_name)
            self.regist_image.close()
            self.regist_image.flush()
            print("Slice for registration saved")

# other functions
def open_czi_series(file_name, series_number, rect=False):
    # TODO: implement the selection of only one channel (not necessary)
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


def get_data_structure(seriesCount):
    num_of_real_images = seriesCount - 2  # TODO: make this with a checkbox in the gui
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


def get_core_names(file_names, core_name):
    out_names = []
    for name in file_names:
        if core_name in name:
            # parse for the Slices
            name_pieces = name.split('_')
            mr_index_array = [i for i, s in enumerate(name_pieces) if 'manualROI-' in s]
            # check that there is only one occurrence
            if len(mr_index_array) == 1:
                out_names.append('_'.join(name_pieces[0:(mr_index_array[0] + 1)]))
            else:
                raise NameError('Your file name should not contain slice-')
    return set(out_names)


def extractChannel(imp, nChannel, nFrame):
    """ Extract a stack for a specific color channel and time frame """
    stack = imp.getImageStack()
    ch = ImageStack(imp.width, imp.height)
    for i in range(1, imp.getNSlices() + 1):
        index = imp.getStackIndex(nChannel, i, nFrame)
        ch.addSlice(str(i), stack.getProcessor(index))
    stack_to_return = ImagePlus("Channel " + str(nChannel), ch)
    stack_to_return.copyScale(imp)
    return stack_to_return


def get_corners(roi, L):
    # get the points inside roi
    poly = roi.getContainedFloatPoints()
    xs = poly.xpoints
    ys = poly.ypoints
    # create an empty set to hold the corners
    corners = set()
    for x, y in zip(xs, ys):
        # add the modulo of the size to set
        # need to be tuple, lists can't be adde to a set
        xc = x - x % L
        yc = y - y % L
        corners.add((xc, yc))

    return corners


def overlay_corners(corners, L):
    ov = Overlay()
    for [x, y] in corners:
        rect = Roi(x, y, L, L)
        rect.setStrokeColor(Color.RED)
        rect.setLineWidth(2)
        ov.add(rect)
    return ov


def overlay_roi(roi, ov):
    roi.setStrokeColor(Color.GREEN)
    roi.setLineWidth(4)
    ov.add(roi)
    return ov


def clean_corners(corners, roi, L):
    # get the points inside roi
    poly = roi.getContainedPoints()
    xs = [int(p.getX()) for p in poly]
    ys = [int(p.getY()) for p in poly]
    points = zip(xs, ys)
    corners_cleaned = set()
    for c in corners:
        if c in points:  # if the corner is inside
            if (c[0] + L, c[1] + L) in points:  # if the opposite corner is inside
                if (c[0] + L, c[1]) in points:
                    if (c[0], c[1] + L) in points:
                        corners_cleaned.add(c)
    # sort rois first by x and then by y coordinates
    return sorted(sorted(corners_cleaned, key=lambda item: item[1]))


def write_roi_numbers(ov, corners, L):
    fontsize = int(L / 1.5)
    roiID = 1
    for [x, y] in corners:
        text = TextRoi(x, y, L, L, str(roiID), Font("Arial", Font.BOLD, fontsize))
        text.setJustification(2)
        text.setColor(Color.RED)
        ov.add(text)
        roiID += 1
    return ov


if __name__ == '__main__':
    gui()
# Fiji_Custom
Fiji scripts

## CZI_SlideScanner_ROIsubdivider
Deals with the huge .czi files produced by Slide scanner. Currently it works for the RNAscope pipeline in CellProfiler_AnalysisPipelines. 
It opens the low resolution image of the selected set of piramidal images, gets the manually-drawn ROI and subdivides it into smaller squared ones, saving the channels separately and saving summary and ROIs. It also opens a higher resolution image (TODO: make this selectable by the user) to evaluate the quality (e.g. focus) of the plane. It also saves a ~25um/px version of the slice to register it to the ARA (see Histology_to_ARA repo).

After this is done for every image in the dataset, use Group_convert_and_enhace.py, which transforms the images into 8-bit and normalizes the intensities by channel and by animal

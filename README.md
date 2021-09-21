# Fiji_Custom
Fiji scripts

## CZI_SlideScanner_ROIsubdivider
Deals with the huge .czi files produced by Slide scanner. Currently it works for the RNAscope pipeline in CellProfiler_AnalysisPipelines. 
It opens the low resolution image of the selected set of piramidal images, gets the manually-drawn ROI and subdivides it into smaller squared ones, saving the channels separately and saving summary and ROIs. It also opens a higher resolution image (TODO: make this selectable by the user) to evaluate the quality (e.g. focus) of the plane. It also saves a ~25um/px version of the slice to register it to the ARA (see Histology_to_ARA repo).

After this is done for every image in the dataset, use Group_convert_and_enhace.py, which transforms the images into 8-bit and normalizes the intensities by channel and by animal

# Workflow for registration and analysis of PH3 data
1. Use 'Save_resolution_and_channel_from_czi.py' in Fiji to export slices. (Using channel 4 and 5um/px atm)
2. Register using ABBA and save transformation field and atlas annotations: https://biop.github.io/ijp-imagetoatlas/registration.html#slices-registration
  - Flip the axis as the ABBA atlas is the other way around (check this once registration is made)
  - Save inside the same folder as the original images

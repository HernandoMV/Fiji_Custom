# Fiji_Custom
Fiji scripts

## CZI_SlideScanner_ROIsubdivider
Deals with the huge .czi files produced by Slide scanner. Currently it works for the RNAscope pipeline in CellProfiler_AnalysisPipelines. 
It opens the low resolution image of the selected set of piramidal images, gets the manually-drawn ROI and subdivides it into smaller squared ones, saving the channels separately and saving summary and ROIs. It also opens a higher resolution image (TODO: make this selectable by the user) to evaluate the quality (e.g. focus) of the plane. It also saves a ~25um/px version of the slice to register it to the ARA (see Histology_to_ARA repo).

After this is done for every image in the dataset, use Group_convert_and_enhace.py, which transforms the images into 8-bit and normalizes the intensities by channel and by animal


# Workflow for quantifying lesions
0. This assumes image acquisition with at least 2 channels (DAPI and NeuN) or slices that are well oriented in DV
  - Make sure the name of the .czi files is 'Animal-X-Y-Z_Experimental-Procedure_slide-X.czi
  - The underscores are very important. Don't have spaces. The last part (e.g. '..._slide-1') is also crucial.
1. Use 'Save_resolution_two-channels_from_czi.py in Fiji. 10um/px resolution
2. Register with ABBA as in the workflow above, but DO NOT tilt the atlas much.
3. Get the lesioned area with get_lesion_area.py
4. Register ROIs to ARA with register_ROIs_to_ARA.py
5. Quantify the lesions using quantify_lesions.py
6. Plot and visualise results using load_lesion_stacks.py and plot_lesions.py

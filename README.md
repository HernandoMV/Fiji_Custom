# Fiji_Custom
Fiji scripts

## CZI_SlideScanner_ROIsubdivider
Deals with the huge .czi files produced by Slide scanner. Currently it works for the RNAscope pipeline in CellProfiler_AnalysisPipelines. 
It opens the low resolution image of the selected set of piramidal images, gets the manually-drawn ROI and subdivides it into smaller squared ones, saving the channels separately and saving summary and ROIs. It also opens a higher resolution image (TODO: make this selectable by the user) to evaluate the quality (e.g. focus) of the plane. It also saves a ~25um/px version of the slice to register it to the ARA (see Histology_to_ARA repo).

After this is done for every image in the dataset, use Group_convert_and_enhace.py, which transforms the images into 8-bit and normalizes the intensities by channel and by animal

# Workflow for registration and analysis of PH3 data
0. This assumes an acquisition of data with 4 channels in the slide scanner at 20x.
  - Make sure the name of the .czi files is 'Animal-X-Y-Z_Experimental-Procedure_slide-X.czi
  - The underscores are very important. Don't have spaces. The last part (e.g. '..._slide-1') is also crucial.
1. Use 'Save_resolution_and_channel_from_czi.py' in Fiji to export slices. (Using channel 4 and 10um/px atm)
2. Register using ABBA and save transformation field and atlas annotations: https://biop.github.io/ijp-imagetoatlas/registration.html#slices-registration
  - Create a folder called 'QuPath' inside the 'Registration' folder just created by the previous script
  - Open QuPath, and drag the folder to create a new project. Add the images created by the script, selecting BioFormats-builder. Close QuPath.
  - Open ABBA in Fiji and import the QuPath project.
  - Flip the axis as the ABBA atlas is the other way around
  - Register once with affine, using channel 1 of the atlas (autofluorescence). Set the proper background value!
  - Register with spline with 10 landmarks, also correcting background and correct registration
  - Export regions to file, and export atlas coordinates to imageJ.
  - Save inside the same folder as the original images
3. Use 'CZI_SlideScanner_ROIsubdivider to generate the ROIs, loading the region of interest (e.g. Caudoputamen)
  - TODO: think about removing the part of the image that is not inside the ROI
    - Then I can make this automatic and without the need to have a GUI
4. Use 'Group_convert_and_enhace.py', which transforms the images into 8-bit and normalizes the intensities by channel and by animal
5. Use 'ImageSequence_Downsampler.ijm' to make a copy of both the DARPP-32 channels and the tdTomato (d2) channels in different directories (needed for cellfinder). Do not downsample as we are acquiring at 20x.
6. Run cellpose (https://github.com/MouseLand/cellpose) on both directories: e.g. python -m cellpose --dir /home/hernandom/data/Microscopy_Data/Plasticity/PH3_inmuno/Processed_data/PH308/ROIs--Gce_processed--downsized-1_fileend-2.tif/ --save_tif --no_npy --diameter 38 --pretrained_model cyto --chan 0 --use_gpu
7. Run Inmuno_4channels_XXXXXX.cpproj in CellProfiler_protocols, inside the CellProfiler_AnalysisPipelines repo.
8. Run the notebook Inmuno_4channels_analysis.ipynb, inside the CellProfiler_AnalysisPipelines repo, for each mouse.


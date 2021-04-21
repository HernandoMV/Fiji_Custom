how_much_to_resize = 3;
file_ending = "2.tif";


inputdir = getDirectory("Select Directory containing your data");
setBatchMode(true);

outputdir = File.getParent(inputdir) + 
			File.separator + 
			File.getName(inputdir) + 
			"--downsized-" + 
			how_much_to_resize + 
			File.separator;

File.makeDirectory(outputdir);

files = getFileList(inputdir);
for (i = 0; i < files.length; i++) {
	
	if (files[i].endsWith(file_ending)) {
		open(inputdir + files[i]);
		tit = getTitle();

		getDimensions(width, height, channels, slices, frames);
		xy_scale = 1 / how_much_to_resize;
		new_w = floor(width / how_much_to_resize);
		new_h = floor(height / how_much_to_resize);
		//print(new_h);
		run("Scale...", "x=" + xy_scale + " y=" + xy_scale + 
			" width=" + new_w + " height=" + new_h +
			" interpolation=Bilinear average create title=downsized");
		
		selectWindow("downsized");
		saveAs("Tiff", outputdir + tit);
		run("Close All");
		print(i + '/' + files.length);
	}
}
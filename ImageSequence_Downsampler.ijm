
setBatchMode(true);
outputdir = "/C:/Users/herny/Desktop/ilastik_test/downsampled_rois/";
inputdir = "/C:/Users/herny/Desktop/ilastik_test/raw_rois/";

files = getFileList(inputdir);
for (i = 0; i < files.length; i++) {
	
	if (files[i].endsWith('.tif')) {
		open(inputdir + files[i]);
		tit = getTitle();
		//print(tit);
		run("Scale...", "x=0.3 y=0.3 width=691 height=691 interpolation=Bilinear average create title=downsized");
		selectWindow("downsized");
		saveAs("Tiff", outputdir + tit);
		run("Close All");
		print(i + '/' + files.length);
	}
	
	//print(files[i]);
}

/*

selectWindow("img_0000.tiff");
run("Scale...", "x=0.2 y=0.2 width=1467 height=1819 interpolation=Bilinear average");
close();
selectWindow("img_0000.tiff");
run("Scale...", "x=0.2 y=0.2 width=1467 height=1819 interpolation=Bilinear average create title=downsized");
saveAs("Tiff", "/home/hernandom/Desktop/Downsized_TH/img_0000.tiff");
*/


setBatchMode(true);
outputdir = "/home/hernandom/Desktop/Downsized_TH/";
inputdir = "/home/hernandom/Desktop/WholeBrain_642nm_TH/";

files = getFileList(inputdir);
for (i = 0; i < files.length; i++) {
	open(files[i]);
	tit = getTitle();
	run("Scale...", "x=0.2 y=0.2 width=1467 height=1819 interpolation=Bilinear average create title=downsized");
	selectWindow("downsized");
	saveAs("Tiff", outputdir + tit);
	run("Close All");
	print(i + '/' + files.length);
}

/*

selectWindow("img_0000.tiff");
run("Scale...", "x=0.2 y=0.2 width=1467 height=1819 interpolation=Bilinear average");
close();
selectWindow("img_0000.tiff");
run("Scale...", "x=0.2 y=0.2 width=1467 height=1819 interpolation=Bilinear average create title=downsized");
saveAs("Tiff", "/home/hernandom/Desktop/Downsized_TH/img_0000.tiff");
*/

dir = getDirectory("Select Directory containing your data");
print("Working in this directory: " + dir);
//get the list of the files in the directory
filesindir = getFileList(dir);
print(filesindir.length + " files in directory");
//go through the files one by one
for (i=0; i < filesindir.length; i++){
	open(dir + filesindir[i]);
	name = getTitle();
	run("Make Montage...", "columns=4 rows=1 scale=1");
	saveAs("tif", dir + name + "_montage.tif");
	close(name + "_montage.tif");
	print(i + '/' + filesindir.length);
	close(name);
}
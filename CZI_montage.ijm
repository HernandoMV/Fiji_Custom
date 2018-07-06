//assumes files are in order for the montage
//two colors for now

run("Close All");
//setBatchMode(true);

dir = getDirectory("Select Directory containing the Signal Probability Map");
//dir = "C:/Users/herny/Desktop/SWC/Data/CorticoStriatal_Projections/MouseLinesCharacterization/607250_AxioZoom_20180706/Overview_slide_A_mCh/";
print("Working in this directory: " + dir);
//get the list of the files in the directory
filesindir = getFileList(dir);
//go through the files one by one
for (i=0;i<filesindir.length;i++){
	//open if raw
	if (endsWith(filesindir[i],".czi")){
		print("Opening " + filesindir[i]);
		run("Bio-Formats (Windowless)", "open=" + dir + filesindir[i]);
		ImageInProgress = getTitle();	
		//split channels
		run("Split Channels");		
	}
}

//make a stack with the images of the first channel
run("Images to Stack", "name=C1_stack title=C1 use");
//rotate 180
run("Rotate... ", "angle=180 grid=1 interpolation=Bilinear stack");
//make a stack with the images of the second channel
run("Images to Stack", "name=C2_stack title=C2 use");
//rotate 180
run("Rotate... ", "angle=180 grid=1 interpolation=Bilinear stack");


//make a montage
CustomMontage("C1_stack");
C1tit = getTitle();
CustomMontage("C2_stack");
C2tit = getTitle();

setBatchMode(false);
//merge the channels
run("Merge Channels...", "c1=" + C1tit + " c2=" + C2tit + " create");



function CustomMontage(StackTit){
	selectWindow(StackTit);
	sln = nSlices();

	if (sln<101){
		colnum = 10;
		rownum = 10;		
	}
	if (sln<82){
		colnum = 9;
		rownum = 9;		
	}
	if (sln<65){
		colnum = 8;
		rownum = 8;		
	}
	if (sln<50){
		colnum = 7;
		rownum = 7;		
	}		
	if (sln<43){
		colnum = 7;
		rownum = 6;		
	}
	if (sln<37){
		colnum = 6;
		rownum = 6;		
	}
	if (sln<31){
		colnum = 6;
		rownum = 5;		
	}		
	if (sln<26){
		colnum = 5;
		rownum = 5;		
	}
	if (sln<21){
		colnum = 5;
		rownum = 4;		
	}
	if (sln<17){
		colnum = 4;
		rownum = 4;		
	}
	if (sln<13){
		colnum = 4;
		rownum = 3;		
	}
	if (sln<10){
		colnum = 3;
		rownum = 3;		
	}
	if (sln<7){
		colnum = 3;
		rownum = 2;		
	}
	if (sln<5){
		colnum = 2;
		rownum = 2;		
	}
	if (sln<3){
		colnum = 2;
		rownum = 1;		
	}
	if (sln<2){
		colnum = 1;
		rownum = 1;		
	}

	montstr = "columns="+colnum+" rows="+rownum+" scale=1 first=1 last="+sln+" increment=1 border=0 font=12";
	run("Make Montage...", montstr);
	rename(StackTit + "_CustomMontage");
	selectWindow(StackTit);
	close();
}


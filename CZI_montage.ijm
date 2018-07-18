//assumes files are in order for the montage
//any number of channels should be taken
//TO DO:
//Determine automatically parameters for the text?
//Test for one channel

run("Close All");
//setBatchMode(true);

//Parameters:
angleToRot = 180;
positionOfName = 2; //1,2 correspond to TopLeft, TopMiddle (only TopMiddle working at the moment).
TextSize = 60;

dir = getDirectory("Select Directory containing your data");
//dir = "C:/Users/herny/Desktop/SWC/Data/CorticoStriatal_Projections/MouseLinesCharacterization/700325_AxioZoom_20180709/";
print("Working in this directory: " + dir);
//get the list of the files in the directory
filesindir = getFileList(dir);
//go through the files one by one
counter = 0;
for (i=0; i < filesindir.length; i++){
	//open if raw
	if (endsWith(filesindir[i],".czi")){
		print("Opening " + filesindir[i]);
		run("Bio-Formats (Windowless)", "open=" + dir + filesindir[i]);
		//get image name
		ImageInProgress = getTitle();
		stringToWrite = File.getName(ImageInProgress);
		//rotate
		run("Rotate... ", "angle=" + angleToRot + " grid=1 interpolation=Bilinear stack");
		//get info about the data
		if (counter==0){
			getDimensions(width, height, channels, slices, frames);
		}	
		//split channels if there is more than one
		if (channels > 1){
			run("Split Channels");
		}else{
			rename("C1-" + ImageInProgress);
		}
		//add name to channel 1
		WriteName ("C1-" + ImageInProgress, stringToWrite, positionOfName);
		counter += 1;
	}
}
print("Number of channels = " + channels);
//setBatchMode(false);
//make a montage for each of the channels
MCstring = ""; //string for merging the channels later
for (j=1; j <= channels; j++){
	//make a stack with the images of the first channel
	run("Images to Stack", "name=C" + j + "_stack title=C" + j + " use");	
	//make a montage
	CustomMontage("C" + j + "_stack");
	//string for merging the channels
	MCstring = MCstring + "c" + j + "=" + getTitle() + " ";
}

//merge the channels
run("Merge Channels...", MCstring + "create");
rename(File.getName(dir) + "_CZIMontage");


function WriteName (imname, string, position){
	selectWindow(imname);
	setFont("SansSerif" , TextSize, "bold");
	setJustification("center");
	setColor(255, 255, 255);
	//determine the position of the string
	if (position == 2){
		posx = getWidth()/2;
		posy = 150;
	}
	drawString(string, posx, posy);
}

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


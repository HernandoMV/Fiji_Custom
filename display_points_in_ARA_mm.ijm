//modified from:
// This macro builds a 3D sphere in an image stack.
// Check 'Surface only' to get only the surface of the sphere.
// Authors: G. Hernan Sendra and Holger Lorenz
// ZMBH University of Heidelberg, Germany

macro "display_points_in_ARA" {
// Default values
Radius = 3;
// laptop:
ARA = "/C:/Users/herny/Desktop/SWC/Data/Anatomy/ARA_25_micron_mhd/template.mhd";
// nailgun:
ARA = "/home/hernandom/data/Anatomy/ARA_25_micron_mhd/template.mhd";
FileDir = File.openDialog("choose the csv file");
atlas_resolution = 25; //microns per pixel
R = pow(Radius,2);

setBatchMode(false);

lineseparator = "\n";
cellseparator = ",";

// copies the whole RT to an array of lines
lines=split(File.openAsString(FileDir), lineseparator);

// open the ARA template
open(ARA);
selectWindow("template.raw");
//reverse
run("Reverse");

getDimensions(Width, Height, channels, Slices, frames);

newImage("undetermined", "16-bit black", Width, Height, Slices);
newImage("spn", "16-bit black", Width, Height, Slices);
newImage("d1", "16-bit black", Width, Height, Slices);
newImage("d2", "16-bit black", Width, Height, Slices);

for (i = 1; i < lines.length; i++) {
	//print(lines[i]);
	showProgress(i/lines.length);
	items=split(lines[i], cellseparator);
	cell_label=items[3];
	//print(cell_label);
	selectImage(cell_label);
	//information is in millimeters, in order ap, dv, -ml
	trans_value = 1000 / atlas_resolution;
	flipped_x0 = floor(parseFloat(items[2]) * trans_value); 
	y0 = floor(parseFloat(items[1]) * trans_value); 
	z0 = floor(parseFloat(items[0]) * trans_value);
	//flip ml
	x0 = Width - flipped_x0;

	for (x=(x0-R);x<=(x0+R);x++) {
		for (y=(y0-R);y<=(y0+R);y++) {
			for (z=(z0-R);z<=(z0+R);z++) {
				if (pow(x-x0,2)+pow(y-y0,2)+pow(z-z0,2) <= R) {
					setSlice(z+1);
					setPixel(x,y,5000);
				}	
			}	
		}
	}	
}

selectImage("template.raw");
run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
run("Grays");
//run("Divide...", "value=2.5 stack");

//str2merch = "c1=spn c2=d1 c3=d2 c4=template.raw c5=undetermined create";

//run("Merge Channels...", str2merch);
//selectImage(cell_label);
setBatchMode(false);
//setBatchMode("show");
//selectImage(cell_label);
//selectImage("d1");
//this needs modification
selectImage("template.raw");
run("Z Project...", "start=280 stop=280 projection=[Sum Slices]");
rename("atlas_slice");

selectImage("d1");
run("Z Project...", "start=260 stop=300 projection=[Sum Slices]");
rename("d1_proj");
//run("Fire");
selectImage("d2");
run("Z Project...", "start=260 stop=300 projection=[Sum Slices]");
rename("d2_proj");

str2merch = "c1=d1_proj c2=d2_proj c3=atlas_slice create";
run("Merge Channels...", str2merch);
}


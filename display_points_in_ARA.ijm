//modified from:
// This macro builds a 3D sphere in an image stack.
// Check 'Surface only' to get only the surface of the sphere.
// Authors: G. Hernan Sendra and Holger Lorenz
// ZMBH University of Heidelberg, Germany

macro "display_points_in_ARA" {
// Default values
Radius = 1;
ARA = "/C:/Users/herny/Desktop/SWC/Data/Anatomy/ARA_25_micron_mhd/template.mhd";
FileDir = File.openDialog("choose the csv file");
resolution = 1; //info is in pixels
R = pow(Radius,2);

setBatchMode(true);

lineseparator = "\n";
cellseparator = ",";

// copies the whole RT to an array of lines
lines=split(File.openAsString(FileDir), lineseparator);

// open the ARA template
open(ARA)
selectWindow("template.raw");
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
	
	x0 = floor(parseFloat(items[0])) * resolution; 
	y0 = floor(parseFloat(items[1])) * resolution; 
	z0 = floor(parseFloat(items[2])) * resolution;
	//print(x0);

	for (x=(x0-R);x<=(x0+R);x++) {
		for (y=(y0-R);y<=(y0+R);y++) {
			for (z=(z0-R);z<=(z0+R);z++) {
				if (pow(x-x0,2)+pow(y-y0,2)+pow(z-z0,2) <= R) {
					setSlice(z+1);
					setPixel(x,y,30000);
				}	
			}	
		}
	}	
}

selectImage("template.raw");
run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
run("Grays");
//run("Divide...", "value=2.5 stack");

str2merch = "c1=spn c2=d1 c3=d2 c4=template.raw c5=undetermined create";

run("Merge Channels...", str2merch);

setBatchMode(false);

run("Z Project...", "start=230 stop=260 projection=[Sum Slices]");
run("Fire");

}


/*  Split_Channels_Montage
 *  20180915
 *  Hernando Martinez
 *  
 *  This script takes a composite (multi-channel) tif image and creates a montage with the channels
 *  separated and an overlay of all of them
 */

/*
 * TO DO:
 * - Add scale bar
 * - Select which channels to include - Use the order array in the for loops
 * - abort if image is not correct (1 channel)
 * - Include a list of all LUTs
 * - Make a better name without the tif in the middle
 */
run("Close All");

//Select composite file 
path = File.openDialog("Choose a File");
filedir = File.getParent(path); //not used at the moment
//open file and get title name
open(path);
imtit = getTitle();
//read parameters to use them in the dialog
getDimensions(width, height, channels, slices, frames);

//create a dialog
//Specify arrays
LUT_array = newArray("Grays", "Cyan", "Red", "Green", "Fire"); //Include new LUTs here
Channel_names = newArray("DAPI", "SPNs", "D2", "PH3", "Ch5", "Ch6", "Ch7"); //Defaults names to write
Order_array = newArray(channels); //for the order of the channels
for (i=1; i<=channels; i++){ //loop for default values
	Order_array[i-1] = i;
}
Order_array = Array.concat(Order_array,0); //composite last
//dialog title
Dialog.create("Select the LUTs and names to display");
//add one choice for LUT and name for every channel
for (i=1; i<=channels; i++){
	Dialog.addChoice("C"+i, LUT_array, LUT_array[i-1]);
	Dialog.addString("C"+i+" name:", Channel_names[i-1]);
}
//choices for the single channel images
Dialog.addCheckbox("Use LUTs for single channels?", true);
Dialog.addChoice("Single channels LUT (ignored if checked above)", LUT_array);
//order for the single channels left to right
Dialog.addString("Write the order of the montage (0 is composite):", ArrayToString(Order_array,","));
Dialog.show();

//get the LUTs for the Composite pictures and the names
ListOfLuts = newArray(channels);
ListOfNames = newArray(channels);
for (i=0; i<ListOfLuts.length; i++){
	ListOfNames[i] = Dialog.getString();
	ListOfLuts[i] = Dialog.getChoice();
}
//LUTs for Single Channels
SingleChannelsLUTCheck = Dialog.getCheckbox(); //if same LUTs as in Composite
SingleChannelsLUT = Dialog.getChoice(); //If different LUT for the individual channels
ListOfSingleChannelsLUT = ListOfLuts;
/*
ListOfSingleChannelsLUT = newArray(channels);
for (i=0; i<ListOfSingleChannelsLUT.length; i++){
	if (SingleChannelsLUTCheck==true){
		ListOfSingleChannelsLUT[i] = ListOfLuts[i];
	}
	else {
		ListOfSingleChannelsLUT[i] = SingleChannelsLUT;
	}
}
*/
//order array conversion
Order_array = split(Dialog.getString(),',');

//create a composite in RGB
selectWindow(imtit);
run("Duplicate...", "duplicate");
rename("im1");
//write names before RGB so they are in the same LUT
yposition = round(getHeight*0.95);
for(i=1; i<=channels; i++){
	//Change LUT
	setSlice(i);
	run(ListOfLuts[i-1]);
	print(ListOfLuts[i-1]);
	//write names
	WriteName (getTitle, ListOfNames[i-1], round(getWidth*0.05), yposition, i);
	yposition = yposition - round(getHeight*0.05);
}
run("RGB Color");
rename("im2");
//Add Scale Bar
TextSize = round(getHeight/25);
run("Scale Bar...", "width=50 height=5 font="+TextSize+" color=White background=None location=[Lower Right] bold overlay");
run("Flatten"); //not sure if this is necessary
rename("C0-" + imtit); //for the order

close("im1");
close("im2");

//split the channels
selectWindow(imtit);
run("Split Channels");

//for each channel, change the LUT and write the name
for (i=1; i<=channels; i++){
	selectWindow("C"+i+"-"+imtit);
	rename("remove this");
	run(ListOfSingleChannelsLUT[i-1]);
	print("C"+i+"-"+imtit);
	print(ListOfSingleChannelsLUT[i-1]);
	//Write name
	WriteName (getTitle, ListOfNames[i-1], round(getWidth*0.05), round(getHeight*0.95), 1);
	run("Flatten"); //flatten if there is overlay
	rename("C"+i+"-"+imtit);
	selectWindow("remove this");
	run("Close");	
}
//make montage: keep combining the images in the order specified
Montage_image = "C"+Order_array[0]+"-"+imtit;
//DO THE FOR LOOP WITH THE ORDER ARRAY INSTEAD
for(i=1; i<Order_array.length; i++){
	run("Combine...", "stack1=" + Montage_image + " stack2=C"+Order_array[i]+"-"+imtit);
	rename("Combined");
	Montage_image = "Combined";
}
//MAKE A BETTER NAME
rename(imtit + "Split_Channels_Montage");



function ArrayToString(myArr, delim){
	//This function converts an array to a string, with the values separated by a delimiter (delim)
	myStr = "";
	for(i=0; i<(myArr.length-1); i++){
		myStr = myStr + myArr[i] + delim;
	}
	myStr = myStr + myArr[myArr.length-1];
	return myStr;
}


function WriteName (imname, string, posx, posy, slicenum){
	//This function writes, in 'imname', in slice 'slicenum', a 'string' in 'posx' and 'posy'
	//It selects a proportional text size.
	selectWindow(imname);
	TextSize = round(getHeight/15);
	setFont("SansSerif" , TextSize, "bold");
	setJustification("left");
	setColor(255, 255, 255);
	setSlice(slicenum);
	drawString(string, posx, posy);
}
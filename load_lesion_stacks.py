from ij import IJ
from ij.plugin import ImageCalculator, Duplicator
import os
import glob

FILE_ENDING = 'lesion-in-atlas-interpolated.tif'

ATLAS_FILE = '/home/hernandom/data/Anatomy/ARA_25_micron_mhd/template.tif'
# ATLAS_FILE = r'C:\Users\herny\Desktop\SWC\Data\Anatomy\ARA_25_micron_mhd\template.tif'

if __name__ in ['__builtin__', '__main__']:
    IJ.run("Close All")
    # get a directory
    input_path = IJ.getDirectory('choose a path containing your processed animals')
    # get a list of the animals analised
    animals_in_folder = os.listdir(input_path)
    # list of lesions stacks paths
    stacks_list = []
    for folder in animals_in_folder:
        files = glob.glob(os.path.join(input_path, folder, '*' + FILE_ENDING))

        if len(files) > 1:
            print('Something weird in folder {}'.format(folder))

        for file in files:
            print('Found file for animal {}'.format(folder))
            # get if it is a lesion or control
            if os.path.basename(file).split('_')[1] == 'lesion':
                print('    it is a lesioned animal.')
                stacks_list.append(file)

    # open atlas
    atlas = IJ.openImage(ATLAS_FILE)
    IJ.run(atlas, "Reverse", "")
    # create an equal image
    grouped_lesions = IJ.createImage("lesions", "8-bit black",
                                     atlas.getWidth(), atlas.getHeight(), atlas.getNSlices())
    grouped_lesions.show()
    # number of animals
    n_ans = len(stacks_list)
    div_str = "value=" + str(n_ans) + " stack"
    # open each stack and divide
    for stack_path in stacks_list:
        stack = IJ.openImage(stack_path)
        stack.show()
        IJ.run(stack, "Divide...", div_str)
        # add it to the grouped lesions
        ImageCalculator.run(grouped_lesions, stack, "Add stack")
        # close
        IJ.selectWindow(stack.getTitle())
        IJ.run("Close")  
        #stack.close()
        #stack.flush()

    # TODO: overlay hunnicutt / AUD projections

    # overlay onto the atlas
    atlas.show()
    IJ.run(atlas, "8-bit", "")
    IJ.run(atlas, "Invert", "stack")
    IJ.run(grouped_lesions, "Fire", "")
    IJ.run("Merge Channels...", "c1=template.tif c2=lesions create")
    IJ.selectWindow("Composite")
    comp_im = IJ.getImage()
    # close stuff
    atlas.close()
    grouped_lesions.close()

    # TODO: take image samples and make composite
    imp2 = Duplicator().run(comp_im, 1, 2, 281, 281, 1, 1)
    IJ.run(imp2, "Stack to RGB", "")
    imp2.close()
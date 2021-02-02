# Hernando M. Vergara, SWC
# Feb 2021
# image_manipulation.py
# generic functions

from ij import ImagePlus, ImageStack


def extractChannel(imp, nChannel, nFrame):
    """ Extract a stack for a specific color channel and time frame """
    stack = imp.getImageStack()
    ch = ImageStack(imp.width, imp.height)
    for i in range(1, imp.getNSlices() + 1):
        index = imp.getStackIndex(nChannel, i, nFrame)
        ch.addSlice(str(i), stack.getProcessor(index))
    stack_to_return = ImagePlus("Channel " + str(nChannel), ch)
    stack_to_return.copyScale(imp)
    return stack_to_return

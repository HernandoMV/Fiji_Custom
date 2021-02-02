# Hernando M. Vergara, SWC
# Feb 2021
# roi_and_ov_manipulation.py
# generic functions to manipulate ROIs and overlays

from ij.gui import Roi, TextRoi, PolygonRoi, Overlay
from java.awt import Label, Color, Font


def get_corners(roi, L):
    # get the points inside roi
    poly = roi.getContainedFloatPoints()
    xs = poly.xpoints
    ys = poly.ypoints
    # create an empty set to hold the corners
    corners = set()
    for x, y in zip(xs, ys):
        # add the modulo of the size to set
        # need to be tuple, lists can't be adde to a set
        xc = x - x % L
        yc = y - y % L
        corners.add((xc, yc))

    return corners


def overlay_corners(corners, L):
    ov = Overlay()
    for [x, y] in corners:
        rect = Roi(x, y, L, L)
        rect.setStrokeColor(Color.RED)
        rect.setLineWidth(2)
        ov.add(rect)
    return ov


def overlay_roi(roi, ov):
    roi.setStrokeColor(Color.GREEN)
    roi.setLineWidth(4)
    ov.add(roi)
    return ov


def clean_corners(corners, roi, L):
    # get the points inside roi
    poly = roi.getContainedPoints()
    xs = [int(p.getX()) for p in poly]
    ys = [int(p.getY()) for p in poly]
    points = zip(xs, ys)
    corners_cleaned = set()
    for c in corners:
        if c in points:  # if the corner is inside
            if (c[0] + L, c[1] + L) in points:  # if the opposite corner is inside
                if (c[0] + L, c[1]) in points:
                    if (c[0], c[1] + L) in points:
                        corners_cleaned.add(c)
    # sort rois first by x and then by y coordinates
    return sorted(sorted(corners_cleaned, key=lambda item: item[1]))


def write_roi_numbers(ov, corners, L):
    fontsize = int(L / 1.5)
    roiID = 1
    for [x, y] in corners:
        text = TextRoi(x, y, L, L, str(roiID), Font("Arial", Font.BOLD, fontsize))
        text.setJustification(2)
        text.setColor(Color.RED)
        ov.add(text)
        roiID += 1
    return ov

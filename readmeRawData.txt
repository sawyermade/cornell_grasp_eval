The dataset file contains 5 types of files:
1. Image files
	Named pcdxxxxr.png
	where xxxx ranges from 0000-1034
	These are the original images of the objects
2. Point cloud files
	Named pcdxxxx.txt
	where xxxx ranges from 0000-1034
3. Handlabeled grasping rectangles
	Named pcdxxxxcpos.txt for positive rectangles
	Named pcdxxxxcneg.txt for negative rectangles
4. Background images
	Named pcdb_xxxx.png
5. A mapping from each image to its background image
	Named backgroundMapping.txt
	
====================================================
2. Point cloud files
Point cloud files are in .PCD v.7 point cloud data file format
See http://www.pointclouds.org/documentation/tutorials/pcd_file_format.php
for more information. Each uncommented line represents a pixel in the image.  That point in space that intersects that pixel (from pcdxxxxr.png) has x, y, and z coordinates (relative to the base of the robot that was taking the images, so for our purposes we call this "global space").  

You can tell which pixel each line refers to by the final column in each line (labelled "index").  That number is an encoding of the row and column number of the pixel. In all of our images, there are 640 columns and 480 rows.  Use the following formulas to map an index to a row, col pair.  Note that index = 0 maps to row 1, col 1.

row = floor(index / 640) + 1
col = (index MOD 640) + 1

3. Grasping rectangle files contain 4 lines for each rectangle. Each line
contains the x and y coordinate of a vertex of that rectangle separated by a space. The first two coordinates of a rectangle define the line
representing the orientation of the gripper plate. Vertices are listed in
counter-clockwise order.

5. The backgroundMapping file contains one line for each image in the 
dataset, giving the image name and the name of the corresponding
background image separated by a space.

Obviously, in non-research settings, you would not want to force your personal robot to take a background picture beforehand, so this is not a practical way to handle identifying objects.  However, for the sake of concentrating only on grasping, it is a very convenient method to subtract the backgrounds when possible.

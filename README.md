This tool tries to provide an easy way of representing data on maps, the input data is provided in the form of a json but there is a parser for excel files (atm it still needs some work, if the field in excel is not a a value but a formula is can not parse it). 

To use the tool you first need to get a mask image of the map you'll want to use, its better if the map is one color. Input the name of the image file in ImageName.txt. Then run the preapere mask script. In the output image the map region should be fully collored and the areas around the map should be transparent. You can tweak the Inverse and Threashold values in PreapereMask.py till you have the desired result.

Once you have the mask, you need to calibrate the map to real life coordinates. Run the Calibration script, with the mouse and arrow keys select a point on the map, then on google maps select the right click on the same point and copy the coordinates, paste them into the input field on the program and submit the points. Repeat for the second point. Its better if points are far appart horizontally and vertically.

Then either parse the data from an excel file or import your json. And run the dataDysplay.py script. 

This is still an alpha version so its usable but may have alot of bugs and isnt really polished. This is my school project.

To use this tool you need to have python installed and these libs: pillow, tkinter, scypy, pyopencl, numpy, screeninfo, openpyxl
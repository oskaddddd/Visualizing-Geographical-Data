This tool tries to provide an easy way of representing data on maps, the input data is provided in the form of a json but there is a parser for excel files (atm it still needs some work, if the field in excel is not a a value but a formula is can not parse it). 

To use the tool you first need to get a mask image of the map you'll want to use, its better if the map is one color. Input the name of the image file in ImageName.txt. Then run the preapere mask script. In the output image the map region should be fully collored and the areas around the map should be transparent. You can tweak the Inverse and Threashold values in PreapereMask.py till you have the desired result.

Once you have the mask, you need to calibrate the map to real life coordinates. Run the Calibration script, with the mouse and arrow keys select a point on the map, then on google maps select the right click on the same point and copy the coordinates, paste them into the input field on the program and submit the points. Repeat for the second point. Its better if points are far appart horizontally and vertically.

Then either parse the data from an excel file or import your json. And run the dataDysplay.py script. 

This is still an alpha version so its usable but may have alot of bugs and isnt really polished. This is my school project.

To use this tool you need to have python installed and these libs: pillow, tkinter, scypy, pyopencl, numpy, screeninfo, openpyxl

settings.json:
-ImageName: The name of the mask image.
-Mode:
    0 - Black and White (white - high, black - low)
    1 - RGB (Red - high, Green - mid, Blue - low)
    2 - RG (Green - high, Red - Low)
    3 - RB (Red - high, Blue - low)
-CreateAgenda: True or false, weather you want to create a legend.
-AgendaVerticalAlignment: A value from 0 to 1, where 0 is the top of the image, 1 is bottom and for example 0.5 is the middle.
-AgendaHorizontalAlignment: Left or right.
-AgendaOffsetFromMap: How many pixels the legend is offset from the map.
-AgendaScale: How big the legend is compared to the map image, for example with a value of 0.5, the legend would be half as big as the map.
-AgendaSteps: How many sections will the agenda be devided into.
-AgendaTextScale: How big the text is compared to a single section in the legend.
-AgendaRoundDataTo: How many digits to leave after the comma in agenda text.

Compiled version download: https://mega.nz/file/LJdCgT4a#Ty-Lf7OvDl6xyg6ocmzBWN4al5blQtY2x7JM0t7WoPA

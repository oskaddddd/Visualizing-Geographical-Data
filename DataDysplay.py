from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings

#Get image name


    
settings = ReadSettings.Settings(True)
imageName = settings["ImageName"]

    
print(settings)
#calibration
cali = []

#Get calibration data
try:
    with open('CoordinateCalibration.json',) as f:
        cali = json.load(f)
        if cali == [[[0, 0], 0], [[0, 0], 0]]:
            exit()
except:
    print('Please set 2 calibration coordinates in Calibration.py')
    exit()
    
#Calculate the decoding values
cali[0]['GPS'].reverse()
cali[1]['GPS'].reverse()

k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])),
     (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
b = [cali[0]['Pixel'][0]-(k[0]*float(cali[0]['GPS'][0])),
     cali[0]['Pixel'][1]-(k[1]*float(cali[0]['GPS'][1]))]
print(cali, k, b)

#Decoding function
def Decode(cords:list):
    return [round(float(cords[1])*k[0]+b[0]), round(float(cords[0])*k[1]+b[1])]


data = []

image = PIL.Image.open(imageName)

t2 = time.time()
with open('data.json', 'r') as f:
    data = json.load(f)
mapData = []

for x in data:
    #if t["Pixel"][0] < image.size[0] and t["Pixel"][1] < image.size[1] and t["Pixel"][0] > 0 and t["Pixel"][1] > 0:
    n = Decode(x["GPS"])
    mapData.append([n[0], n[1], x["Value"]])

print(time.time()-t2, 'tdttddt')


#Interpolation Function on the gpu
def Interpolate(points):
    print(1)
    t = time.time()
    
    points=np.array(points, dtype=np.uint16)
    Mode = settings["Mode"]
    lenth = None
    res = None
    if settings["Computation"].lower() == 'opencl':
        if settings["Interpolation"].lower() == 'idw':
            creator = Interpolation.InterpolationIDW_GPU(False)
            creator.createBuffers(image.size, points)
            creator.compute()
        else:
            creator = Interpolation.interpolateRandomGpu(True)
            creator.createPixelBuffer(image.size, Image=image)
            lenth = (creator.createTriangles(points=points, Mode=Mode, showTriangles=False)[1:])
            res = creator.compute()
    else:
        creator = Interpolation.interpolateRandomCpu()
        o = creator.createTriangles(points, image.size, True, Image=np.array(image), Mode=Mode, doSectioning=settings["SectionMap"], sections=settings["Sections"])
        res = o[0]
        lenth = (o[1], o[2])

    print(time.time()-t)
    
    if settings["CreateLegend"] == True:
        steps = settings["Sections"]
        textScale = settings["LegendTextScale"]


        barSize = round(image.size[1]/(1.5*steps - 0.5)*settings["LegendScale"])
        Legend = np.zeros((round(steps*barSize*1.5-barSize*0.5), 3*barSize, 4), dtype=np.uint8)

        units = ' '+settings["LegendUnits"]

        textLegend = np.zeros((round(steps*barSize*1.5-barSize*0.5), round(barSize*0.59*textScale*(settings["LegendRoundDataTo"]+len(str(round(lenth[1]))+units)))+10 + (8 if settings["LegendRoundDataTo"] != 0 else 0), 4), dtype=np.uint8)

        print(barSize*textScale, 'wad')
        imText = PIL.Image.fromarray(textLegend)
        drawText = PIL.ImageDraw.Draw(imText)

        font = PIL.ImageFont.truetype("arial.ttf", round(barSize*textScale))
        #font = PIL.ImageFont.load_default()
        for i in range(steps):

            barsColor = None
            if Mode == 0:
                val = round(255*(i/(steps-1)))

                barsColor = np.array([val, val, val, 255])
                #print(barsColor, round(1.5*barSize*(steps-1-i)+barSize), round(1.5*barSize*(steps-1-i)), i/(steps-1), agenda.shape)
            elif Mode == 1:
                k = i/(steps-1)*4

                if k >= 2.7:
                    barsColor = np.array([255, (4-k)*255/1.3, 0, 255])
                elif k >= 2 and k < 2.7:
                    barsColor = np.array([(k-2)*255/4/0.7, 255, 0, 255])
                elif k >= 1.3 and k < 2:
                    barsColor = np.array([0, 255, (2-k)*255/0.7, 255])
                elif k < 1.3:
                    barsColor = np.array([0, k*255/1.3, 255, 255])
                print(k)


            Legend[round(1.5*barSize*(steps-1-i)):round(1.5*barSize*(steps-1-i)+barSize), :barSize*3] = barsColor

            drawText.text((0,round(1.5*barSize*(steps-1-i)+((barSize-(barSize*textScale))/2))), " "+str(round((i/(steps-1))*(lenth[1]-lenth[0])+lenth[0], settings["LegendRoundDataTo"]))+units, font=font)

        textLegend = np.array(imText)
        AgendaObj = np.concatenate((Legend, textLegend), axis=1, dtype=np.uint8)
        #AgendaObj = CreateLegend((l, m), settings["Mode"], image.size, legendScale, legendSteps,  legendTextScale, legendRoundDataTo, legendUnits)
        #print(np.zeros((round((image.size[1]-AgendaObj.shape[0])*legendVerticalAlignment),  AgendaObj.shape[1], 4)).shape, AgendaObj.shape, np.zeros((round((image.size[1]-AgendaObj.shape[0])*(1-legendVerticalAlignment)),  AgendaObj.shape[1], 4)).shape,(image.size[1]-AgendaObj.shape[0])*legendVerticalAlignment, image.size[0])
        AgendaObj = np.concatenate( ( np.zeros((round((image.size[1]-AgendaObj.shape[0])*settings["LegendVerticalAlignment"]),  AgendaObj.shape[1], 4), dtype = np.uint8),\
        AgendaObj, np.zeros((image.size[1] - round((image.size[1]-AgendaObj.shape[0])*settings["LegendVerticalAlignment"]+AgendaObj.shape[0]),  AgendaObj.shape[1], 4),  dtype = np.uint8)))
        
        if settings["LegendHorizontalAlignment"].lower() == 'left':
            res = np.concatenate((AgendaObj, np.zeros((AgendaObj.shape[0], settings["LegendOffsetFromMap"], 4)), res), axis = 1)
        else:
            res = np.concatenate((res,np.zeros((AgendaObj.shape[0], settings["LegendOffsetFromMap"], 4)), AgendaObj), axis = 1)
    #print(res)
    return res.astype(np.uint8)

def InterpolateRandomCpu(points):
    points = np.array(points)
    create = Interpolation.interpolateRandomCpu()
    #print(create.createPixels(image.size, Image=image))
    return create.createTriangles(points, image.size, True, Image=np.array(image))
    

def CreateLegend(lenth, Mode, dimentions, scale, steps, textScale, textRound, units):
    barSize = round(dimentions[1]/(1.5*steps - 0.5)*scale)
    Legend = np.zeros((round(steps*barSize*1.5-barSize*0.5), 3*barSize, 4), dtype=np.uint8)
    
    units = ' '+units
    
    textLegend = np.zeros((round(steps*barSize*1.5-barSize*0.5), round(barSize*0.59*textScale*(textRound+len(str(round(lenth[1]))+units)))+10 + (8 if textRound != 0 else 0), 4), dtype=np.uint8)

    print(barSize*textScale, 'wad')
    imText = PIL.Image.fromarray(textLegend)
    drawText = PIL.ImageDraw.Draw(imText)

    font = PIL.ImageFont.truetype("arial.ttf", round(barSize*textScale))
    
    for i in range(steps):
        
        barsColor = None
        if Mode == 0:
            val = round(255*(i/(steps-1)))
            
            barsColor = np.array([val, val, val, 255])
            #print(barsColor, round(1.5*barSize*(steps-1-i)+barSize), round(1.5*barSize*(steps-1-i)), i/(steps-1), agenda.shape)
        elif Mode == 1:
            k = i/(steps-1)*4
            
            if k >= 2.7:
                barsColor = np.array([255, (4-k)*255/1.3, 0, 255])
            elif k >= 2 and k < 2.7:
                barsColor = np.array([(k-2)*255/4/0.7, 255, 0, 255])
            elif k >= 1.3 and k < 2:
                barsColor = np.array([0, 255, (2-k)*255/0.7, 255])
            elif k < 1.3:
                barsColor = np.array([0, k*255/1.3, 255, 255])
            print(k)
            
            
        Legend[round(1.5*barSize*(steps-1-i)):round(1.5*barSize*(steps-1-i)+barSize), :barSize*3] = barsColor

        drawText.text((0,round(1.5*barSize*(steps-1-i)+((barSize-(barSize*textScale))/2))), " "+str(round((i/(steps-1))*(lenth[1]-lenth[0])+lenth[0], textRound))+units, font=font)
    
    textLegend = np.array(imText)
    out = np.concatenate((Legend, textLegend), axis=1, dtype=np.uint8)

    return out
    
            
    #print(agenda)


#Debugging function to see where the points are placed
def ShowPoints(Points):
    imageArr = np.array(image)
    for x in Points:
        imageArr[x["Pixel"][1]][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]+1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]-1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]+1] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]-1] = [255, 0, 0, 255]
    PIL.Image.fromarray(imageArr).show()

t = time.time()
#cpuArr = InterpolateRandomCpu(mapData)
print(time.time()-t)
arr = Interpolate(mapData)
PIL.Image.fromarray(arr).show()


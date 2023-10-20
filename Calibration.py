import PIL.Image
import PIL.ImageTk
import numpy as np
from tkinter import *
import json
from screeninfo import get_monitors
import time
import ReadSettings

monitor = get_monitors()[0]
monitor = (monitor.width, monitor.height)

print(monitor)
imageName = ReadSettings.Settings(True)["ImageName"]


defImage = PIL.Image.open(imageName).convert('RGBA')
imageScale = min((monitor[1]-200)/defImage.size[1], (monitor[0]-500)/defImage.size[0])
print(imageScale, monitor[1], defImage.size[1])

image = defImage.resize((round(defImage.size[0]*imageScale), round(defImage.size[1]*imageScale)))
#raise the threshold not the entire region is green and lower it if pixels outside the region are green
defjson = [{"GPS": [0, 0], "Pixel" :[0, 0]} for _ in range(2)]
defImageArr = np.array(image)
imageArr = defImageArr.copy()
print("Loaded image into array")

print("Prepearing GUI... This might take abit")

root = Tk()
root.minsize(700, 400)
root.title("Image to real world calibration")

imTK = PIL.ImageTk.PhotoImage(image)

Im = Button(root, image=imTK, borderwidth=0, relief=RAISED)
Info = Label(root, text=f"Enter GPS coordinates for selected pixel {0, 0}, latitude then longitude")

entry = Entry(root, width=40)
selected = [0, 0]
editing = 1 #vars 1 or 2

datList = []
try: 
    with open('CoordinateCalibration.json', 'r') as f:
        datList=json.load(f)
except:
    with open('CoordinateCalibration.json', 'w') as f:
        datList=json.dump(defjson, f, indent=1)
    datList = defjson
print("Read json data")
dat = Label(root, text=f"\n[Pixel position] -- [GPS]\nPoint 1:{datList[0]['Pixel']} -- {datList[0]['GPS']}\nPoint 2:{datList[1]['Pixel']} -- {datList[1]['GPS']}")


tempSelect = [0, 0]
def Selected(e):
    global tempSelect

    tempSelect = [e.x, e.y]
    print('SELECTED', selected)

    Im['relief'] = RAISED

def click():
    global imTK
    global Im
    global imageArr
    global selected

    
    print(f"Registered a click at {selected[0], selected[1]}")
    if tempSelect[1] < image.size[1] and tempSelect[0] < image.size[0]:
        Im['relief'] = RAISED
        if (defImageArr[tempSelect[1]-1][tempSelect[0]-1] == np.array([0, 0, 0, 255])).all():
            selected = [tempSelect[0]-1, tempSelect[1]-1]
            imageArr = np.array(image)
            
            #selected = [selected[0]-1, selected[1]-1]            
            
        
            red = np.array([255, 0, 0, 255])
            imageArr[selected[1]][selected[0]] = red
            imageArr[selected[1]+1][selected[0]] = red
            imageArr[selected[1]-1][selected[0]] = red
            imageArr[selected[1]][selected[0]+1] = red
            imageArr[selected[1]][selected[0]-1] = red
            print("Set pressed pixels to red")
            
            imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
            Im["image"] = imTK
            
            Info['text'] = f"Enter GPS coordinates for selected pixel {round(selected[0]/imageScale), round(selected[1]/imageScale)}, latitude then longitude"
            #Info.grid(row=2, column=0)   
            
            print('Updated Image and Coordinate dysplay')

    print('CLICK', selected)
def resizeImage(e):
    global imageScale
    global image
    global imageArr
    global imTK
    global selected
    global Im
    

    temp = min((e.height-200)/defImage.size[1], (e.width-500)/defImage.size[0])
    if temp == imageScale:
        return
    
    print(e, imageScale, temp)
    
    selected = [round(selected[0] * (temp/imageScale)), round(selected[1] * (temp/imageScale))]
    image = defImage.resize((round(defImage.size[0]*temp), round(defImage.size[1]*temp)))
    #imageArr = np.array(image) 
    #
    #red = np.array([255, 0, 0, 255])
    #imageArr[selected[1]][selected[0]] = red
    #imageArr[selected[1]+1][selected[0]] = red
    #imageArr[selected[1]-1][selected[0]] = red
    #imageArr[selected[1]][selected[0]+1] = red
    #imageArr[selected[1]][selected[0]-1] = red

    imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
    Im["image"] = imTK
    imageScale = temp
delayReset = 0.1
delay = time.time()   
def move(dir):
    global selected
    global imTK
    global delay
    
    if time.time() >= delay:
        delay = time.time()+delayReset
        t = dir
        if t[1] < image.size[1] and t[0] < image.size[0]:
            Im['relief'] = RAISED
            if (defImageArr[t[1]][t[0] ] == np.array([0, 0, 0, 255])).all():
                selected = t
                imageArr = np.array(image)

                #selected = [selected[0]-1, selected[1]-1]            


                red = np.array([255, 0, 0, 255])
                imageArr[selected[1]][selected[0]] = red
                imageArr[selected[1]+1][selected[0]] = red
                imageArr[selected[1]-1][selected[0]] = red
                imageArr[selected[1]][selected[0]+1] = red
                imageArr[selected[1]][selected[0]-1] = red
                print("Set pressed pixels to red")

                imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
                Im["image"] = imTK

                Info['text'] = f"Enter GPS coordinates for selected pixel {round(selected[0]/imageScale), round(selected[1]/imageScale)}, latitude then longitude"
                #Info.grid(row=2, column=0) 
def moveRight(e):
    move([selected[0]+1, selected[1]])
def moveLeft(e):
    move([selected[0]-1, selected[1]])
def moveUp(e):
    move([selected[0], selected[1]-1])
def moveDown(e):
    move([selected[0], selected[1]+1])
    
def CordSubmit():
    global dat
    global datList
    t = entry.get()
    a = []
    if ', ' in t:
        a = t.split()
        #print(1, a[0], len(a)-1)
        a[0] = a[0][:len(a[0])-1]
        
    elif ','in t and ' ' not in t:
        a = [t[:t.index(',')], t[t.index(',')+1:]]
        #print(2)
    elif ',' not in t and ' ' in t:
        a = t.split()
        #print(3)
    print('DEBUG', selected) 
    datList[editing-1]['GPS'] = a
    datList[editing-1]['Pixel'] = [round(selected[0]/imageScale), round(selected[1]/imageScale)]
    print('DEBUG', selected)
    print(f"Read data {t.split()}")
    
    dat['text'] = f"\n[Pixel position] -- [GPS]\nPoint 1:{datList[0]['Pixel']} -- {datList[0]['GPS']}\nPoint 2:{datList[1]['Pixel']} -- {datList[1]['GPS']}"
    print("Dysplayed new data")
    
    with open('CoordinateCalibration.json', 'w') as f:
        json.dump(datList, f, indent=1)
    print("Wrote data to file")
    
    entry.delete("0","end")
    print("Cleared entry field")
        
butt = Button(root, text="Submit coordinates for point 1", command=CordSubmit)
  
def Test(e=None):
    print('GJKLSHGKFJHSDKFHJ')  
def edit():
    global editing
    global butt
    
    
    editing = 1 if editing == 2 else 2
    print(f"Changed curent editing point to point {editing}")
    butt['text'] = f"Submit coordinates for point {editing}"
    #butt.grid(row=4, column=0)
    print("Updated button text")
 
butt1 = Button(root, text=f"Change Point", command=edit)
Im['command'] = click

Info.grid(row=2, column=0)
entry.grid(row=3, column=0)
butt.grid(row=4, column=0)
Im.grid(row=1, column=0)
butt1.grid(row=5, column=0)
dat.grid(row=1, column=1)
print("Loaded widgets")

root.bind('<Button 1>',Selected)
#root.bind('<ButtonRelease 1>', click)
root.bind('<Configure>', resizeImage)
root.bind('<Right>', moveRight)
root.bind('<Left>', moveLeft)
root.bind('<Up>', moveUp)
root.bind('<Down>', moveDown)

print("Starting window...")
root.mainloop()

import pyopencl as cl
import numpy as np
from scipy.spatial import Delaunay
import math
import os
os.environ['PYOPENCL_NO_CACHE'] = '1'



class interpolateRandomGpu():
    def __init__(self, interactive = False) -> None:
        self.ctx = cl.create_some_context(interactive=interactive)
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
    def createPixelBuffer(self, resolution = None, Points = None, Image =None) -> list: #width, height
        Dots = []
        if resolution != None and Points == None:
            x_coords = np.arange(resolution[0])
            y_coords = np.arange(resolution[1])
            xx, yy = np.meshgrid(x_coords, y_coords)
            Dots = np.dstack((xx, yy, np.zeros_like(xx)))
            self.res = np.ones((resolution[1], resolution[0], 4), dtype=Dots.dtype)
        
        #print(self.res.shape, Dots.shape)  
        self.pixels = Dots
        self.pixelBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = Dots.nbytes)
        cl.enqueue_copy(self.queue, self.pixelBuffer, self.pixels)
        
        self.destBuffer = cl.Buffer(self.ctx, flags = self.mf.WRITE_ONLY, size = self.res.nbytes)
        
        imageArr = np.array(Image, dtype=Dots.dtype)
        self.imageBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = imageArr.nbytes)
        cl.enqueue_copy(self.queue, self.imageBuffer, imageArr)
        #print(imageArr)
         
        #print(Dots.nbytes, self.pixels.nbytes, Dots.nbytes*2, 'lajkshflkahsjl;kkksskkssklalala')
        self.image = Image
        return Dots
    
    def createTriangles(self, points, Mode = 0 ,showTriangles = False):
        '''Modes:\n
        0 - Black and White (white - high, black - low)\n
        1 - RGB (Red - high, Green - mid, Blue - low)\n
        2 - RG (Green - high, Red - Low)\n
        3 - RB (Red - high, Blue - low)'''
        #ogPoints = points.copy()
        p = points[:, 2]
        points = points[:, :2]
        
        m = math.ceil(max(p))
        l = math.floor(min(p))

        tri = Delaunay(points)
        
        output = np.empty((tri.simplices.shape[0], 3, 3), dtype=self.pixels.dtype)

        for i, simplex in enumerate(tri.simplices):
            triangle = [np.array([points[index][0], points[index][1], p[index]]) for index in simplex]
            output[i] = triangle
        #print(output)

        #output = np.array(output)
        
        self.triangles = output
        self.triBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = output.nbytes)
        cl.enqueue_copy(self.queue, self.triBuffer, self.triangles)
        
        #size0, size1, sizeZ, sizeTri, maxVal, minVal, mode
        self.data = np.array([self.image.size[0], self.image.size[1], 3, int(self.triangles.size/9),m, l, Mode])
        self.sizeBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.data.nbytes)
        cl.enqueue_copy(self.queue, self.sizeBuffer, self.data)
        return (output, m, l)
    
    def compute(self):
        programSource = ''
        with open('interpolation.c', 'r') as f:
            programSource = f.read()
            
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.Bilinear(self.queue, (self.data[0], self.data[1]), None, self.triBuffer, self.destBuffer, self.sizeBuffer, self.imageBuffer)
        
        cl.enqueue_copy(self.queue, self.res, self.destBuffer)
        return self.res


class interpolateRandomCpu():

    def createTriangles(self, points, resolution, clip = True, Image = None, Mode = 0, doSectioning = False, sections = 4):
        

        '''Modes:\n
        0 - Black and White (white - high, black - low)\n
        1 - RGB (Red - high, Green - mid, Blue - low)\n
        2 - RG (Green - high, Red - Low)'''
        
        
        #ogPoints = points.copy()
        p = points[:, 2]
        
        
        points = points[:, :2]
        
        m = math.ceil(max(p))
        l = math.floor(min(p))
        dif = (m-l)/255

        sectionList = np.empty((6), dtype=np.int64)
        if doSectioning:
            sectionList[0:sections-1] = np.arange(0, m-l, (m-l)/(sections-1), dtype=np.uint8)
            sectionList[sections-1] = m-l

        print(sectionList, m-l)

        tri = Delaunay(points)
        
        output = np.empty((tri.simplices.shape[0], 3, 3), dtype=np.int32)
        imageOutput = np.zeros(shape=(resolution[1], resolution[0], 4), dtype = np.uint8)

        for i, simplex in enumerate(tri.simplices):
            triangle = [np.array([points[index][0], points[index][1], p[index]]) for index in simplex]
            output[i] = triangle

        
        
        for triangle in output:
            triangle = triangle[triangle[:, 0].argsort()][::1]
            #if triangle[0][0]>= resolution[0]:
            #    break
            
            if triangle[1][0]-triangle[0][0]!= 0: 
                k01 = (triangle[1][1]-triangle[0][1])/(triangle[1][0]-triangle[0][0])
            else: k01 = None
            
            if triangle[1][0]-triangle[2][0]!= 0: 
                k12 = ((triangle[1][1]-triangle[2][1])/(triangle[1][0]-triangle[2][0])) 
            else: k12 = None
            
            if triangle[2][0]-triangle[0][0]!= 0: 
                k02 = ((triangle[0][1]-triangle[2][1])/(triangle[0][0]-triangle[2][0])) 
            else: k02 = None

            r01 = 0
            r12 = 0
            r02 = 0

            if k01 != None:
                r01 = triangle[1][1]-triangle[1][0]*k01
            if k12 != None:
                r12 = triangle[1][1]-triangle[1][0]*k12
            if k02 != None:
                r02 = triangle[0][1]-triangle[0][0]*k02

            def middle(a, b, c):
                if b>a and b<c:
                    return b
                elif b<a:
                    return a
                else: return c

            xRanges = [middle(0, triangle[0][0], resolution[0]), \
                    middle(0, triangle[1][0], resolution[0]), \
                    middle(0, triangle[2][0], resolution[0])]
           

            for x in range(xRanges[0], xRanges[1]):
                yRange = [middle(0, math.ceil(k01*x+r01), resolution[1]), middle(0, math.ceil(k02*x+r02), resolution[1])]
                if yRange[1]<yRange[0]:
                    y0 = yRange[0]
                    yRange[0] = yRange[1]
                    yRange[1]= y0
                yList = np.arange(start=yRange[0], stop = yRange[1])
                for y in yList:
                    if Image[y][x][3] == 0:
                        continue

                    a = abs(triangle[0][0]*(triangle[1][1]-y) + triangle[1][0]*(y-triangle[0][1]) + x*(triangle[0][1]-triangle[1][1]))
                    b = abs(triangle[0][0]*(y-triangle[2][1]) + x*(triangle[2][1]-triangle[0][1]) + triangle[2][0]*(triangle[0][1]-y))
                    c = abs(x*(triangle[1][1]-triangle[2][1]) + triangle[1][0]*(triangle[2][1]-y) + triangle[2][0]*(y-triangle[1][1]))
                    val = (triangle[2][2]*a+triangle[1][2]*b+triangle[0][2]*c)/(a+b+c)
                    if doSectioning:
                        val = sectionList[(np.abs(sectionList - val)).argmin()]
                    if Mode == 0:
                        val = (val-l)/dif
                        imageOutput[y][x] = np.array([val, val, val, 255])
                    elif Mode == 1:
                        val-=l
                        out = np.array((0, 0, 0, 255))
                        p = (m-l)*0.25

                        if (val >= p*2.7):
                            out[1] = round((((p*4)-val)/(p*1.3))*255)
                            out[0] = 255
                        
                        elif (val >= p*2 and val < p*2.7):
                            out[0] = round(((val-p*2)/(p*0.7))*255)
                            out[1] = 255
                        
                        elif(val >= p*1.3 and val < p*2):
                            out[2] = round(((2*p-val)/(p*0.7))*255)
                            out[1] = 255
                        
                        if (val < p*1.3):
                            out[1] = round((val/(p*1.3))*255)
                            out[2] = 255
                        imageOutput[y][x] = out

                #ranges[i] = np.array((x, math.ceil(k01*x+r01), math.floor(k02*x+r02)))
                i+=1
            for x in range(xRanges[1], xRanges[2]):
                yRange = [middle(0, math.ceil(k12*x+r12), resolution[1]), middle(0, math.ceil(k02*x+r02), resolution[1])]
                if yRange[1]<yRange[0]:
                    y0 = yRange[0]
                    yRange[0] = yRange[1]
                    yRange[1]= y0
                yList = np.arange(start=yRange[0], stop = yRange[1])
                #print(yList[0], yList[yList.shape[0]-1], "ylistRanges")
                for y in yList:
                    if Image[y][x][3] == 0:
                        continue
                    
                    a = abs(triangle[0][0]*(triangle[1][1]-y) + triangle[1][0]*(y-triangle[0][1]) + x*(triangle[0][1]-triangle[1][1]))
                    b = abs(triangle[0][0]*(y-triangle[2][1]) + x*(triangle[2][1]-triangle[0][1]) + triangle[2][0]*(triangle[0][1]-y))
                    c = abs(x*(triangle[1][1]-triangle[2][1]) + triangle[1][0]*(triangle[2][1]-y) + triangle[2][0]*(y-triangle[1][1]))
                    val = (triangle[2][2]*a+triangle[1][2]*b+triangle[0][2]*c)/(a+b+c)
                    if doSectioning:
                        val = sectionList[(np.abs(sectionList - val)).argmin()]
                    #print(val)
                    if Mode == 0:
                        val = round((val-l)/dif)
                        imageOutput[y][x] = np.array([val, val, val, 255])
                    elif Mode == 1:
                        val-=l
                        out = np.array((0, 0, 0, 255))
                        p = (m-l)*0.25

                        if (val >= p*2.7):
                            out[1] = round((((p*4)-val)/(p*1.3))*255)
                            out[0] = 255
                        
                        elif (val >= p*2 and val < p*2.7):
                            out[0] = round(((val-p*2)/(p*0.7))*255)
                            out[1] = 255
                        
                        elif(val >= p*1.3 and val < p*2):
                            out[2] = round(((2*p-val)/(p*0.7))*255)
                            out[1] = 255
                        
                        if (val < p*1.3):
                            out[1] = round((val/(p*1.3))*255)
                            out[2] = 255
                        imageOutput[y][x] = out
                        


                #ranges[i] = np.array((x, math.ceil(k12*x+r12), math.floor(k02*x+r02)))
                i+=1
            #print(triangle)
            #print(ranges, triangle, r01, r12, r02, k01)
            

            

        #output = np.array(output)
        
        self.triangles = output
        return (imageOutput, m, l)


        
class InterpolationIDW_GPU():
    def __init__(self, interactive = False) -> None:
        self.ctx = cl.create_some_context(interactive=interactive)
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
    def createBuffers(self, resolution = None, Points = None) -> list: #width, height
        #self.resolution = np.array((len(Points), resolution[0], resolution[1]), dtype=np.uint16)
        self.resolution = np.array((5, 5, 5), dtype=np.uint16)
        
        self.dist = np.zeros(self.resolution, dtype=np.uint16)
        print(self.dist.nbytes)
        self.distBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_WRITE, size = self.dist.nbytes)
        
        self.pointsBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = Points.nbytes)
        self.resBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.resolution.nbytes)
        
        cl.enqueue_copy(self.queue, self.pointsBuffer, Points)
        cl.enqueue_copy(self.queue, self.resBuffer, self.resolution)
    

    
    def compute(self):
        programSource = ''
        with open('interpolation2.c', 'r') as f:
            programSource = f.read()
            
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.CalculateDistances(self.queue, self.resolution, None, self.resBuffer, self.pointsBuffer, self.distBuffer)

        cl.enqueue_copy(self.queue, self.dist, self.distBuffer)
        print(self.dist)



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
        programSource = """
    kernel void Bilinear(global int *triangles, global int *out, global int *data, global int *Image) {
        
        int g1 = get_global_id(1);
        int g0 = get_global_id(0);

        int index = g1 * data[0] * data[2] + g0 * data[2];
        int indexOut = g1*data[0]*4+g0*4;
        int i = 0;
        
        if (Image[indexOut + 3] == 255){
            for (i = 0; i < data[3]; i++){
                int tri[9];
                int i1 = 0;
                for (i1 = 0; i1 < 9; i1++){
                    tri[i1] = triangles[i1+i*9];
                }

                float a = fabs((float)tri[0]*(tri[4]-tri[7]) + tri[3]*(tri[7]-tri[1]) + tri[6]* (tri[1]-tri[4]));
                float a1 = fabs((float)g0*(tri[4]-tri[7]) + tri[3]*(tri[7]-g1) + tri[6]* (g1-tri[4]));
                float a2 = fabs((float)tri[0]*(g1-tri[7]) + g0*(tri[7]-tri[1]) + tri[6]* (tri[1]-g1));
                float a3 = fabs((float)tri[0]*(tri[4]-g1) + tri[3]*(g1-tri[1]) + g0* (tri[1]-tri[4]));

                if(fabs((a1 + a2 + a3) -a) < 0.0001){
                    int A = tri[2];
                    int B = tri[5];
                    int C = tri[8];

                    float n = ((A*a1+B*a2+C*a3)/(a1+a2+a3))-data[5];
                    if (data[6] == 0){
                        float o = n*(255/(data[4]-data[5]));
                        out[indexOut] = o;
                        out[indexOut+1] = o;
                        out[indexOut+2] = o;
                        out[indexOut+3] = 255;
                    }
                    else if (data[6] == 1){
                        float p = (data[4]-data[5])*0.25;

                        if (n >= p*2.7){
                            out[indexOut+1] = (((p*4)-n)/(p*1.3))*255;
                            out[indexOut] = 255;
                        }
                        else if (n >= p*2 && n < p*2.7){
                            out[indexOut] = ((n-p*2)/(p*0.7))*255;
                            out[indexOut+1] = 255;
                        }
                        else if (n >= p*1.3 && n < p*2){
                            out[indexOut+2] = ((2*p-n)/(p*0.7))*255;
                            out[indexOut+1] = 255;
                        }
                        if (n < p*1.3){
                            out[indexOut+1] = (n/(p*1.3))*255;
                            out[indexOut+2] = 255;
                        }
                        out[indexOut+3] = 255;
                    }
                    else if (data[6] == 2){
                        float p = (data[4]-data[5])*0.5;
                        if (n >= p){
                            out[indexOut] = 255;
                            out[indexOut+1] = (p*2-n)/p * 255;
                        }
                        else if (n < p){
                            out[indexOut+1] = 255;
                            out[indexOut] = (n)/p * 255;
                        }
                        out[indexOut+3] = 255;
                    }
                    else if (data[6] == 3){
                        float p = (data[4]-data[5])*0.5;
                        if (n > p){
                            out[indexOut] = 255;
                            out[indexOut+2] = (p*2-n)/p * 200;
                        }
                        else if (n < p){
                            out[indexOut+2] = 200;
                            out[indexOut] = n/p * 255;
                        }
                        out[indexOut+3] = 255;
                    }

                    break;
                }
            }
            if(out[indexOut+3] != 255){
                out[indexOut] = Image[indexOut];
                out[indexOut+1] = Image[indexOut+1];
                out[indexOut+2] = Image[indexOut+2];
                out[indexOut+3] = Image[indexOut+3];
            }
        }
    }
"""
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.Bilinear(self.queue, (self.data[0], self.data[1]), None, self.triBuffer, self.destBuffer, self.sizeBuffer, self.imageBuffer)
        
        cl.enqueue_copy(self.queue, self.res, self.destBuffer)
        return self.res
    def Blur(self):
        source = '''kernel void Blur(
            '''

class interpolateRandomCpu():

    def createTriangles(self, points, resolution, clip = True, Image = None, Mode = 0):
        

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
        dif = (m-l)/255

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
            #x, y01/y02, y02
            #ranges = np.zeros(shape = (xRanges[2]-xRanges[0]+1, 3), dtype=np.uint8)

            #if k01 == None and triangle[1][0] < resolution[0]:
            #    #ranges[0] = np.array([triangle[0][0], triangle[0][1], triangle[1][1]])
            #    yList = np.arange(middle(0, triangle[0][1], resolution[1]-1), middle(0, triangle[1][1], resolution[1]-1))
#
            #    for y in yList:
            #        val = triangle[0][2]
            #        imageOutput[y][triangle[1][0]] = np.array([val, val, val, 255])
            #if k12 == None and triangle[1][0] < resolution[0]:
            #    yList = np.arange(middle(0, triangle[1][1], resolution[1]-1), middle(0, triangle[2][1], resolution[1]-1))
            #    #if yList.shape[0]>0:
            #    #    print(yList[0], yList[yList.shape[0]-1], "ylistRanges")
#
            #    for y in yList:
            #        val = triangle[0][2]
            #        imageOutput[y][triangle[1][0]] = np.array([val, val, val, 255])
            i = 0
            #print(xRanges)

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
                    val = round(((triangle[2][2]*a+triangle[1][2]*b+triangle[0][2]*c)/(a+b+c)-l)/dif)
                    imageOutput[y][x] = np.array([val, val, val, 255])

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
                    val = round(((triangle[2][2]*a+triangle[1][2]*b+triangle[0][2]*c)/(a+b+c)-l)/dif)
                    #print(val)
                    imageOutput[y][x] = np.array([val, val, val, 255])
                #ranges[i] = np.array((x, math.ceil(k12*x+r12), math.floor(k02*x+r02)))
                i+=1
            #print(triangle)
            #print(ranges, triangle, r01, r12, r02, k01)
            

            

        #output = np.array(output)
        
        self.triangles = output
        return imageOutput


class interpolateSquaresNumpy():
    def createPixels(self, resolution = None, Points = None, Image =None) -> list: #width, height
        Dots = []

        if resolution != None and Points == None:
            x_coords = np.arange(resolution[0])
            y_coords = np.arange(resolution[1])
            xx, yy = np.meshgrid(x_coords, y_coords)
            Dots = np.dstack((xx, yy, np.zeros_like(xx)))
            self.res = np.ones((resolution[1], resolution[0], 4), dtype=Dots.dtype)
        
        self.pixels = Dots-1
        self.image = Image-1
        return Dots
    def compute(self):
        sizey = len(Dots)
        sizex = len(Dots[0])
        for y in range(sizey):
            for x in range(sizex):
                ps = [self.Dots[y][x], self.Dots[y][x+1], self.Dots[y+1][x], self.Dots[y+1][x+1]]
                
                



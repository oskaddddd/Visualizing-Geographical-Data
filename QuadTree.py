import numpy as np
import logging as log

log.basicConfig(level=log.INFO)
class Node:
    def __init__(self, xRange = [0, 0], yRange = [0, 0], quad=-1, parent=-1, children=[-1, -1, -1, -1], pointIndex = -1):
        self.quad = quad
        self.parent = parent
        self.children = children
        self.pointIndex = pointIndex
        self.xRange = xRange
        self.yRange = yRange
        self.mid = [abs(xRange[1]-xRange[0])//2, abs(yRange[1]-yRange[0])//2]

    def GetMid(self):
        self.mid = [(self.xRange[0]+(self.xRange[1]-self.xRange[0])//2), (self.yRange[0]+(self.yRange[1]-self.yRange[0])//2)]
    def All(self):
        out = np.array([self.mid[0], self.mid[1], self.quad, self.pointIndex, self.parent, self.children[0], self.children[1], self.children[2], self.children[3]])
        return out
    def Debug(self):
        out = ''
        out += f"xRang:{self.xRange}, yRang:{self.yRange}, Quad:{self.quad}, IsLeaf:{('False, indexes:' +str(self.children))if self.children[0]!= -1 else True}, HasPoint:{False if self.pointIndex == -1 else ('True, Index =' +str(self.pointIndex))}, Parent:{self.parent}"
        return out

class QuadTree:
    def __init__(self, points, xRange, yRange):
        '''
        points - a numpy array of all the points to be inserted into the quad tree

        xRange - [min x value of all the point, max x value of all the points]
        
        yRange - [min y value of all the point, max y value of all the points]

        '''
        self.points = points
        self.debug = 0
        #An array that contains all the nodes in class form,
        #will be flatened later in the flattened function using Node.all() function
        self.tree = [Node(xRange=xRange, yRange=yRange)]
        self.xRange = xRange
        self.yRange = yRange


        #Add a 0 to the end of every embeded array (1, 1, 1) -> (1, 1, 1, 0)
        self.outPoints = np.append(points, np.zeros((points.shape[0], 1)), 1)

        steps = 10

        progBar = len(points)//100
        #Insert each point into the quad tree
        for i, p in enumerate(points):
            log.debug('main - moving to next point...')
            self.InsertPoint(0, i)
        
            #if i % (progBar) == 0:
            #    prog = ((i*steps)//len(points))
            #    print(f'[{prog*"#"}{(steps-prog)*"."}] {i*100/len(points)}%', end='\r')

                

    def InsertPoint(self, nodeIndex, pointIndex):

        #self.debug +=1
        #if self.debug == 20:
        #    exit()
        log.debug('\n***INSERT POINT***\n')
        log.debug(f'point node index: {pointIndex, nodeIndex, self.points[pointIndex]}')
        point = self.points[pointIndex]
        log.debug(f'Node: {self.tree[nodeIndex].All()}')
        #If node is a leaf node
        if self.tree[nodeIndex].children[0] == -1:
            log.debug('1if: 1 is leaf')
            #If the leaf node has any points alreadyy stored in them
            if self.tree[nodeIndex].pointIndex != -1:
                log.debug(f'2if: 3 has points')
                if (self.points[self.tree[nodeIndex].pointIndex][:2] == point[:2]).all():
                    self.outPoints[pointIndex] = np.append(point, nodeIndex)
                    self.outPoints[self.tree[nodeIndex].pointIndex][3] = -1
                    self.tree[nodeIndex].pointIndex = pointIndex
                    return
                self.Subdivide(nodeIndex)
                
                #Determine in which quad the point lies and the index of said node
                childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, point)
                childNodeIndex = self.tree[nodeIndex].children[childQuadIndex]
                log.debug(f'Created Children: {self.tree[childNodeIndex].Debug()}')
                log.debug(f'Updated Node: {self.tree[nodeIndex].Debug()} \n')
                #Recursive InsertPoint top the new node (climb up the tree)
                self.InsertPoint(childNodeIndex, pointIndex)
                

            #If leaf node is empty
            else:
                log.debug(('2if:', 4, 'leaf node is empty'))
                #Save the index of the points to the node and index of the node to the point
                self.tree[nodeIndex].pointIndex = pointIndex
                self.outPoints[pointIndex] = np.append(point, nodeIndex)
                   
        #If node isn't a leaf node
        else:
            
            #Determine in which quad the point lies and the index of said node
            childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, point)
            childNodeIndex = self.tree[nodeIndex].children[childQuadIndex]
            log.debug(('1if:', 2, 'isnt leaf node', childNodeIndex))
            #Recursive InsertPoint top the new node (climb up the tree)
            self.InsertPoint(self.tree[nodeIndex].children[childQuadIndex], pointIndex)
        
        
        


    def Subdivide(self, nodeIndex):

        log.debug('\n***SUBDIVIDE***\n')
        #Create a list of nodes with the parent node of the input node and the correct quad
        childNodes = [Node(parent=nodeIndex, quad=i) for i in range(4)]

        #Set the dimmentsions of the nodes
        childNodes[0].xRange = [self.tree[nodeIndex].mid[0], self.tree[nodeIndex].xRange[1]]
        childNodes[0].yRange = [self.tree[nodeIndex].mid[1], self.tree[nodeIndex].yRange[1]]

        childNodes[1].xRange = [self.tree[nodeIndex].xRange[0], self.tree[nodeIndex].mid[0]]
        childNodes[1].yRange = [self.tree[nodeIndex].mid[1], self.tree[nodeIndex].yRange[1]]

        childNodes[2].xRange = [self.tree[nodeIndex].xRange[0], self.tree[nodeIndex].mid[0]]
        childNodes[2].yRange = [self.tree[nodeIndex].yRange[0], self.tree[nodeIndex].mid[1]]

        childNodes[3].xRange = [self.tree[nodeIndex].mid[0], self.tree[nodeIndex].xRange[1]]
        childNodes[3].yRange = [self.tree[nodeIndex].yRange[0], self.tree[nodeIndex].mid[1]]
        


        #Get the quad in which the parents point now lies
        childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, self.points[self.tree[nodeIndex].pointIndex])
        #Transfer the parents point to child and remove parents point
        print(childQuadIndex, nodeIndex)
        childNodes[childQuadIndex].pointIndex = self.tree[nodeIndex].pointIndex    
        
        for x in range(4):
            childNodes[x].GetMid()
            childNodes[x].children = [-1, -1, -1, -1]
            self.tree.append(childNodes[x])
            self.tree[nodeIndex].children[x]  = len(self.tree)-1    
        
        self.tree[nodeIndex].pointIndex = -1
        log.debug ('Working node data after split')
        log.debug(self.tree[nodeIndex].All())

        




    def GetQuad(self, center, point):
        ##print(center, point)
        #Get the quadraint that a point belongs to acording to the center

        #REVIEW THIS LATER, IT SUQS
        if center[0] <= point[0] and center[1] <= point[1]:
            return 0
        elif center[0] > point[0] and center[1] < point[1]:
            return 1
        elif center[0] >= point[0] and center[1] >= point[1]:
            return 2
        elif center[0] < point[0] and center[1] > point[1]:
            return 3
        else:
            print(f'WHATA FUQ {center, point}')
        


    def Flatten(self, dtype: np.dtype = np.int16):
        out = np.empty((9* len(self.tree)), dtype = dtype)
        for i in range(len(self.tree)):
            out[i*9:i*9+9] = self.tree[i].All()
        return out




def add_rectangle(ax, x_range, y_range, edgecolor='red', facecolor='none'):
    import matplotlib.patches as patches
    """
    Add a rectangle to the given axis.

    Parameters:
    - ax: Matplotlib axis object
    - x_range: List or tuple representing the x-axis range [xMin, xMax]
    - y_range: List or tuple representing the y-axis range [yMin, yMax]
    - edgecolor: Outline color of the rectangle (default: 'red')
    - facecolor: Fill color of the rectangle (default: 'none')
    """
    # Create a rectangle patch
    
    rectangle = patches.Rectangle((x_range[0], y_range[0]), x_range[1] - x_range[0], y_range[1] - y_range[0], edgecolor=edgecolor, facecolor=facecolor)

    # Add the rectangle patch to the axis
    ax.add_patch(rectangle)

def VisualizeTree(tree:QuadTree, points:bool = True, nodes:bool = True):
    import matplotlib.pyplot as plt
    if not points and not nodes:
        return
    fig, ax = plt.subplots()

    # Set axis limits
    ax.set_xlim(tree.xRange[0], tree.xRange[1])
    ax.set_ylim(tree.yRange[0], tree.yRange[1])

    if nodes:
        for node in tree.tree:

            if node.children[0] == -1:
                add_rectangle(ax, node.xRange,node.yRange,"black")
    if points:
        for point in tree.outPoints:
            ax.scatter(point[0], point[1], marker='o', color='red')


    # Display the plot
    plt.show()

def Test(pointCount = 100, xRange = (-1000, 1000), yRange = (-1000, 1000), pointRange = (-1000, 1000), visuliazePoints = True, visuliazeNodes = True):
    points = np.random.randint(pointRange[0], pointRange[1], size=(pointCount, 3))
    quad = QuadTree(points,xRange, yRange)
    
    VisualizeTree(quad, visuliazePoints, visuliazeNodes)

if __name__ == "__main__":
    Test(visuliazePoints=True)

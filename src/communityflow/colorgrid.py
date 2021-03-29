import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
from .sequence import Sequence

def hex2rgb(hexcode):
    h = hexcode.strip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgbstr(t):
    return "rgb{}".format(t).replace(" ", "")

# from: https://stackoverflow.com/a/141943/6519688
def redistribute_rgb(r, g, b):
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return int(gray + x * r), int(gray + x * g), int(gray + x * b)

class ColorGrid:
    _sequence = Sequence(0)
    _name = None
    _cmap = None
    _grid = {}
    
    def __init__(self, name):
        self._name = name
        self._cmap = plt.get_cmap(self._name)
        self._makeGrid()

    def _makeGrid(self):
        for color in self._cmap.colors:
            index = self._sequence()
            self._grid[index] = {}
            self._grid[index]['hex'] = {}
            self._grid[index]['rgb'] = {}

            hexcode = colors.rgb2hex(color)
            r,g,b = hex2rgb(hexcode)

            for tint in range(10, 21):
                v = tint/10
                tr,tg,tb = redistribute_rgb(r*v, g*v, b*v)
                self._grid[index]['hex'][v] = colors.rgb2hex((tr/255,tg/255,tb/255))
                self._grid[index]['rgb'][v] = rgbstr((tr,tg,tb))
                
    def colorFor(self, category, scheme='hex', tint=1.0):
        return self._grid[category][scheme][tint]

    def coloring(self, membership):
        _coloring = []
        for m in membership:
            _coloring.append(self.colorFor(membership[m]))
        return _coloring
    
    def keys(self):
        return self._grid.keys()
    
    def show(self):
        for key in self._grid.keys():
            print(key,self._grid[key])

    def showShades(self):
        someX, someY = 0.0, 0.0
        fig,ax = plt.subplots()
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        currentAxis = plt.gca()

        width = 1.0/len(self._cmap.colors)
        for color in self._cmap.colors:
            hexcode = colors.rgb2hex(color)
            currentAxis.add_patch(Rectangle((someX, someY), width, 1.0,alpha=1, facecolor=hexcode))
            someX += width

        plt.show()
            
    def showTints(self):
        fig,ax = plt.subplots()
        currentAxis = plt.gca()
        ax.set_xlim(1.0, 2.0)
        ax.set_xlabel("Tint Range (1.0 = none)")
        ax.set_yticks(np.arange(0,1,1/len(self._grid)))
        ax.set_yticklabels(np.flip(np.arange(0,len(self._grid)), axis=0))
        ax.set_ylabel("Category\n(community assignment)")
        currentAxis.set_xticks([1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0])

        height = 1.0/len(self._grid)
        width = 1.0/len(self._grid[0]['hex'])
        #print("height:",height,"width:", width)

        Y = 1.0 - height
        for i in self._grid.keys():
            X = 1.0
            for j in self._grid[i]['hex'].keys():
                color = self._grid[i]['hex'][j]
                #print("i: {0:2d}   j: {1:4.1f}   X: {2:4.3f}   Y: {3:4.3f}   color: {4}".format(i,j,X,Y,color))
                currentAxis.add_patch(Rectangle((X, Y), width, height, alpha=1, facecolor=color))
                X += width
            Y -= height

        plt.show()

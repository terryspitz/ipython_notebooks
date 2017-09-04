#Standard setup for functional images using https://mathieularose.com/function-composition-in-python/ and https://docs.python.org/3.1/howto/functional.html

import matplotlib.pyplot as pyplot
import numpy as np
from math import sqrt
import functools
from functools import partial  #supports currying
#functional composition
def compose2(func_1, func_2): return lambda *args, **kwargs: func_1(*func_2(*args, **kwargs))
def compose(*functions): return functools.reduce(compose2, functions)
#define images
width = height = 200
shape=(width,height)
def scaleMove(scale, mx, my): return lambda r,c: (scale*(c/shape[0]+mx), scale*(r/shape[0]+my))
def show(f, scale=1.0, centreX=0.0, centreY=0.0, cmap='bone_r', axes=pyplot): 
    """displays a functional image returning scalar"""
    axes.imshow(np.fromfunction(compose(f, scaleMove(scale*2, centreX-0.5, centreY-0.5)), shape), cmap)
    axes.xaxis.set_major_formatter(pyplot.NullFormatter())
    axes.yaxis.set_major_formatter(pyplot.NullFormatter())
def showC(f, scale=1.0, centreX=0.0, centreY=0.0, axes=pyplot): 
    """displays a functional image returning RGBA components"""
    axes.imshow(np.fromfunction(
        partial(colourTupleToComponent,compose(f, scaleMove(scale*2, centreX-0.5, centreY-0.5))), 
        (height, width, 4)))
    axes.xaxis.set_major_formatter(pyplot.NullFormatter())
    axes.yaxis.set_major_formatter(pyplot.NullFormatter())
def colourTupleToComponent(f,x,y,colourComponent):
    im=f(x,y) ##tuple of nbarrays
    return (colourComponent==0)*im[0] + (colourComponent==1)*im[1] + (colourComponent==2)*im[2] + (colourComponent==3)*im[3]
def red(x,y): return 1,0,0,1
def gradientRB(x,y): return x,0.1,y,1
def gradientGB(x,y): return 0.3,x*0.7+0.3,y,1
def shaded(): return partial(colourTupleToComponent, gradientRG)
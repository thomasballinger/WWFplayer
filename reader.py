import numpy
import matplotlib
from PIL import Image
import pylab
from matplotlib import cm

im = Image.open('ryan3.PNG')

# shows all channels
#pylab.imshow(numpy.hstack(numpy.dsplit(numpy.array(im),4))[:,:,0], cmap=cm.gray); pylab.show()
red, green, blue, alpha = [numpy.squeeze(x)
        for x in numpy.dsplit(numpy.array(im), 4)]

# green appears especially good for identifying letters
# blue is good for white letters (move just made by opponent)

def edgeDetection(image):
    hdeltas = numpy.vstack(numpy.convolve([-1,0,1], line, 'same') for line in image)
    #pylab.imshow(hdeltas)
    #pylab.show()
    vdeltas = numpy.transpose(numpy.vstack(numpy.convolve([-1,0,1], col, 'same') for col in numpy.transpose(image)))
    #pylab.imshow(vdeltas)
    #pylab.show()
    edges = numpy.sqrt(hdeltas**2+vdeltas**2)
    #pylab.imshow(edges)
    #pylab.show()
    return edges
edges = [edgeDetection(red), edgeDetection(green), edgeDetection(blue)]
all_edges = sum(edges)
edges.append(all_edges)
pylab.imshow(numpy.hstack(edges))
pylab.show()

#finding the grid:
horz_grid = numpy.sum(edgeDetection(blue), axis=1)
pylab.plot(horz_grid)
pylab.show()

vert_grid = numpy.sum(edgeDetection(blue), axis=0)
pylab.plot(vert_grid)
pylab.show()

h_fft = numpy.fft.rfft(horz_grid)
#pylab.plot(h_fft)
#pylab.show()

v_fft = numpy.fft.rfft(vert_grid)
#pylab.plot(v_fft)
#pylab.show()

shared = min([h_fft.size, v_fft.size])
both_fft = abs(v_fft[:shared]) + abs(h_fft[:shared])
pylab.plot(both_fft)
pylab.show()

print len(both_fft)
frequencies = zip(numpy.abs(both_fft), range(len(both_fft)))
frequencies.sort(reverse=True)
top_frequency = [freq for value, freq in frequencies if freq > 1][0]
print top_frequency
grid_distance = top_frequency

#next: use phase information to find these squares of grid_distance

# find where the pattern really takes off
print h_fft[top_frequency]
print v_fft[top_frequency]
print numpy.angle(h_fft[top_frequency])
print numpy.angle(v_fft[top_frequency])
h_offset = numpy.angle(h_fft[top_frequency]) / (2*numpy.pi) * top_frequency
v_offset = numpy.angle(v_fft[top_frequency]) / (2*numpy.pi) * top_frequency

grid = numpy.zeros(red.shape)
print top_frequency
for i in range(v_offset, grid.shape[0], top_frequency):
    for j in range(h_offset, grid.shape[1], top_frequency):
        grid[i, j] = 1



pylab.imshow(grid * 500 + red)
pylab.show()






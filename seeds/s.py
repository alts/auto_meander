import numpy

def generate(shape):
    y, x = shape
    cell_grid = numpy.zeros((y - 1, x - 1))
    for yi in xrange(y - 1):
        if yi % 2 == 0:
            cell_grid[yi,:] = 1
        elif (yi // 2) % 2 == 0:
            cell_grid[yi, 0] = 1
        else:
            cell_grid[yi, -1] = 1
    return cell_grid
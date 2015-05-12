import numpy


def shift_down(grid):
    shifted = numpy.roll(grid, 1, axis=0)
    shifted[0,:] = 0
    return shifted


def shift_up(grid):
    shifted = numpy.roll(grid, -1, axis=0)
    shifted[-1,:] = 0
    return shifted


def shift_right(grid):
    shifted = numpy.roll(grid, 1, axis=1)
    shifted[:,0] = 0
    return shifted


def shift_left(grid):
    shifted = numpy.roll(grid, -1, axis=1)
    shifted[:,-1] = 0
    return shifted

import cv2
from grid_ops import shift_up, shift_right, shift_down, shift_left
import numpy
import random


def pick_candidate(candidates):
    y, x = candidates.shape
    num_candidates = numpy.sum(candidates)
    choice_index = random.randint(1, num_candidates) - 1
    skipped_candidates = 0
    for yi in xrange(y):
        for xi in xrange(x):
            if candidates[yi, xi] == True:
                if skipped_candidates == choice_index:
                    return yi, xi
                skipped_candidates += 1


def make_starting_cycle(shape):
    """
    Creates a cycle in an S-like shape, at the specified size.

    This function will return something if given a size that includes an odd
    number of units, but it won't actually be a cycle. This is part bug and part
    intrinsic limitation. I've left it alone, rather than raise an exception,
    because the results are aesthetically pleasing.
    """
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


def mutate(grid):
    """
    Alters the cycle by breaking it into two separate circuits, and then fusing
    them back together to recreate a (slightly different) cycle.

    This operation is called "sliding" in 'An Algorithm for Finding Hamiltonian
    Cycles in Grid Graphs Without Holes', and it's specifically mentioned
    because it is insuffient if you want to be able to reach all possible cycles
    for a given starting graph. That condition isn't really relevant to this
    project, so I use sliding since it's much easier to implement.
    """
    working_grid = grid.copy().astype(numpy.uint8)

    above = shift_down(grid)
    below = shift_up(grid)
    left = shift_right(grid)
    right = shift_left(grid)

    # this mask highlights every grid location that could be turned off
    candidates = numpy.logical_and(
        numpy.logical_and(grid, above != left),
        numpy.logical_and(above == below, left == right)
    )

    # the connected region is split into two
    coord = pick_candidate(candidates)
    flood_y, flood_x = coord
    working_grid[coord] = 0

    # find the right spot to label one of the regions '2'
    if left[coord] == 1:
        flood_x -= 1
    elif right[coord] == 1:
        flood_x += 1
    elif above[coord] == 1:
        flood_y -= 1
    elif below[coord] == 1:
        flood_y += 1

    cv2.floodFill(
        working_grid,
        numpy.zeros([v + 2 for v in grid.shape], dtype=numpy.uint8),
        (flood_x, flood_y),
        2
    )

    above = shift_down(working_grid)
    below = shift_up(working_grid)
    left = shift_right(working_grid)
    right = shift_left(working_grid)

    x_neighbors = left + right
    y_neighbors = above + below

    # this mask highlights every grid location that can fuse the two regions
    # back together while preserving a cycle
    fuse_candidates = numpy.logical_and(
        working_grid == 0,
        numpy.logical_or(
            numpy.logical_and(x_neighbors == 3, y_neighbors == 0),
            numpy.logical_and(x_neighbors == 0, y_neighbors == 3)
        )
    )

    fuse_location = pick_candidate(fuse_candidates)

    grid[coord] = 0
    grid[fuse_location] = 1

    return grid

import cv2
import numpy
import random
from seeds import s

random.seed(0)

XNODES = 16
YNODES = 20

cell_grid = s.generate((YNODES, XNODES))

WHOLE_GRID_FF_MASK = numpy.zeros([v + 2 for v in cell_grid.shape], dtype=numpy.uint8)

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

def mutate(grid):
    working_grid = grid.copy().astype(numpy.uint8)

    above = shift_down(grid)
    below = shift_up(grid)
    left = shift_right(grid)
    right = shift_left(grid)

    # this mask highlights every grid location that could be turned off
    candidates = numpy.logical_and(numpy.logical_and(grid, above != left),
                             numpy.logical_and(above == below, left == right))

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
    else:
        raise Exception('huh?')

    cv2.floodFill(
        working_grid,
        numpy.zeros([v + 2 for v in cell_grid.shape], dtype=numpy.uint8),
        (flood_x, flood_y),
        2
    )

    above = shift_down(working_grid)
    below = shift_up(working_grid)
    left = shift_right(working_grid)
    right = shift_left(working_grid)

    x_neighbors = left + right
    y_neighbors = above + below

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

def create_screen(cell_grid, shape):
    sy, sx = shape
    canvas = numpy.ones((2 * sy - 1, 2 * sx - 1))

    # draw vertices
    for gx in xrange(XNODES):
        for gy in xrange(YNODES):
            canvas[gy * 2, gx * 2] = 0

    assignment_mask = numpy.zeros(canvas.shape)

    # draw top lines
    rolled_down = shift_down(cell_grid)
    should_draw_top_line = numpy.logical_and(cell_grid, rolled_down == 0)
    scaled_top_line = numpy.kron(should_draw_top_line, numpy.array([[0, 1], [0, 0]]))
    assignment_mask[:-1, :-1] = scaled_top_line
    canvas[assignment_mask == 1] = 0

    assignment_mask = numpy.zeros(canvas.shape)

    # draw bottom lines
    rolled_up = shift_up(cell_grid)
    should_draw_bottom_line = numpy.logical_and(cell_grid, rolled_up == 0)
    scaled_bottom_line = numpy.kron(should_draw_bottom_line, numpy.array([[0, 0], [0, 1]]))
    assignment_mask[1:, :-1] = scaled_bottom_line
    canvas[assignment_mask == 1] = 0

    assignment_mask = numpy.zeros(canvas.shape)

    # draw left lines
    rolled_right = shift_right(cell_grid)
    should_draw_left_line = numpy.logical_and(cell_grid, rolled_right == 0)
    scaled_left_lines = numpy.kron(should_draw_left_line, numpy.array([[0, 0], [1, 0]]))
    assignment_mask[:-1, :-1] = scaled_left_lines
    canvas[assignment_mask == 1] = 0

    assignment_mask = numpy.zeros(canvas.shape)

    # draw right lines
    rolled_left = shift_left(cell_grid)
    should_draw_right_line = numpy.logical_and(cell_grid, rolled_left == 0)
    scaled_right_lines = numpy.kron(should_draw_right_line, numpy.array([[0, 0], [0, 1]]))
    assignment_mask[:-1, 1:] = scaled_right_lines
    canvas[assignment_mask == 1] = 0

    return canvas

def print_onto(canvas, screen, alpha):
    return canvas * screen * alpha + (1 - alpha) * canvas

def create_print(design):
    h, w = design.shape

    # the window into which all of the lines will be printed is one unit larger
    # than the meander design itself
    w += 1
    h += 1

    canvas_color = numpy.array([211, 228, 244]) / 256.0
    primary_color = numpy.array([192, 180, 48]) / 256.0
    canvas = numpy.ones((h, w, 3), dtype=numpy.float64) * canvas_color

    # print out window
    screen = numpy.ones((h, w, 3)) * primary_color
    canvas = print_onto(canvas, screen, 0.2)

    # fit the design onto a mask to to get the colors onto the screen
    mask = numpy.ones((h, w))
    mask[:-1, :-1] = design

    screen.fill(1.0)
    screen[mask == 0] *= primary_color
    canvas = print_onto(canvas, screen, 0.25)

    # the second pass is offset by (1, 1) in grid units
    screen = numpy.roll(screen, 1, axis=0)
    screen = numpy.roll(screen, 1, axis=1)
    canvas = print_onto(canvas, screen, 0.1)

    # the final pass is offset by (0.5, 0.5), so we have to scale everything
    canvas = numpy.kron(canvas, numpy.ones((2, 2, 1)))
    screen = numpy.kron(screen, numpy.ones((2, 2, 1)))
    screen = numpy.roll(screen, -1, axis=0)
    screen = numpy.roll(screen, -1, axis=1)
    # and finally, the design screen is rotated 180 degrees
    screen = numpy.rot90(screen, 2)
    canvas = print_onto(canvas, screen, 0.3)

    # add a blank region around canvas
    sy, sx, sd = canvas.shape
    x_buffer = sx // 4
    y_buffer = sy // 4
    padding = min(x_buffer, y_buffer)
    grown_canvas = numpy.ones((sy + padding*2, sx + padding*2, sd), dtype=numpy.float64) * canvas_color
    grown_canvas[padding:-padding,padding:-padding] = canvas
    canvas = grown_canvas

    # scale canvas
    SCALE_FACTOR = 7
    return numpy.kron(canvas, numpy.ones((SCALE_FACTOR, SCALE_FACTOR, 1)))

cumulative = None

LIMIT = 15000

for i in xrange(LIMIT):
    if i % 1000 == 0:
        print '{0} / {1} generations'.format(i, LIMIT)
    cell_grid = mutate(cell_grid)

screen = create_screen(cell_grid, (YNODES, XNODES))

cv2.imshow('meander', create_print(screen))
cv2.waitKey()
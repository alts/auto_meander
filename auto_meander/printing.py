from .grid_ops import shift_up, shift_right, shift_down, shift_left
import numpy


def create_screen(cell_grid, shape):
    sy, sx = shape
    canvas = numpy.ones((2 * sy - 1, 2 * sx - 1))

    # draw vertices
    for gx in range(sx):
        for gy in range(sy):
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


def create_print(design, primary_color):
    h, w = design.shape

    # the window into which all of the lines will be printed is one unit larger
    # than the meander design itself
    w += 1
    h += 1

    canvas_color = numpy.array([211, 228, 244]) / 256.0
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

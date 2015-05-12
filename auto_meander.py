import auto_meander.hamiltonian_cycle as hamiltonian_cycle
import auto_meander.printing as printing
import cv2
import numpy
import os
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option('-r', '--seed', dest='seed',
    help='seed for random number generator. Useful for reproducing interesting designs')
parser.add_option('-s', '--size', dest='size', default='15x19',
    help='dimensions, in grid units, for the design screen in the form "WIDTHxHEIGHT"')
parser.add_option('-m', '--mode', dest='mode', default='save',
    help='either "save" (default) or "show". If "show",  images will be displayed one by one in a popup')
parser.add_option('-n', '--number', dest='number', default='1',
    help='number of images to generate. If a seed is specified, it will apply only to the first generated image')


options, args = parser.parse_args()

# check seed option
if options.seed is not None:
    try:
        seed_value = int(options.seed)
    except ValueError:
        seed_value = options.seed
else:
    seed_value = hash(os.urandom(8))

# check size option
dimensions = options.size.split('x')
if len(dimensions) != 2:
    print 'the "size" argument must be in the form WIDTHxHEIGHT, e.g. 15x19'
    exit(1)

try:
    x_cells, y_cells = map(int, dimensions)
except ValueError:
    print 'the "size" argument must use numbers, e.g. 15x19'
    exit(1)

if x_cells % 2 == 0 or y_cells % 2 == 0:
    print 'both dimensions in "size" must be odd numbers'
    exit(1)

grid_shape = (y_cells + 1, x_cells + 1)

# check number option
try:
    num_images = int(options.number)
except ValueError:
    print 'the "number" argument has to be a number, e.g. 5'
    exit(1)

LIMIT = 15000

for image_i in xrange(num_images):
    print 'generating image {0} of {1}...'.format(image_i + 1, num_images)

    if image_i > 0:
        seed_value = hash(os.urandom(8))
    random.seed(seed_value)

    cell_grid = hamiltonian_cycle.make_starting_cycle(grid_shape)

    for i in xrange(LIMIT):
        if i % 1000 == 0:
            print '\t{0} / {1} generations'.format(i, LIMIT)
        cell_grid = hamiltonian_cycle.mutate(cell_grid)

    screen = printing.create_screen(cell_grid, grid_shape)

    if options.mode == 'show':
        cv2.imshow('meander', printing.create_print(screen))
        cv2.waitKey()
    else:
        try:
            os.mkdir('out')
        except OSError:
            pass

        cv2.imwrite(
            'out/{0}_{1}.png'.format(seed_value, options.size),
            (printing.create_print(screen) * 255).astype(numpy.uint8)
        )

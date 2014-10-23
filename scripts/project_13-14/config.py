#-*- coding: utf-8

import logging 
import os, sys, time
import random
import Image
import ImageDraw
import ImageFont
from PIL import ImageShow
import numpy as np
import scipy.sparse

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__package__)

results_dir = "./"

# INSTRUCTIONS
# Add 'export IVM_DIR=your_ivm_directory' to your environment file
# Do not forget to load it, by doing 'source your_environment_file.env'
try:
    from decoder.image import Imdec
    from descriptor.gists import Gist
    from indexation.exhaustive import ExhaustiveDb
    ivm_dir = os.environ['IVM_DIR']
except:
    print 'Bouuh vilain(e) ! Lis les instructions dans \'config.py\''
    sys.exit(0)

images_dir = os.path.join(ivm_dir, 'Copydays/VisualDatabase')
query_dir = os.path.join(ivm_dir, 'Copydays/Queries')
database_name = 'VisualDatabase.h5'
font_path = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf'

# The parameter that might matter for you is 'knn' below. This is the length
# of the shortlist containing candidate images. You might want to pick from it
# and then do the re-ranking to display the 20 best.
config = { 
    'common': {
        'dir': results_dir,
    },
    'Imdec': {
        'basedir': images_dir,
    },
    'Gist': {
        'image_resize': (64, 64), #resize the image before computing gist
        'power_law': None, #do not apply power-law
        'normalization': "L2", #normalize the vectors using L2 norm
    },
    'ExhaustiveDb': {
        'drop_zero': True, #do not index descriptors of zero norm
        'knn': 100, #number of nearest neighbors to retreive
        'disttype': "L2", #distance between vectors computed using L2 norm
        'dbfile': database_name,
    },
}

# Create the pipeline
image_factory = Imdec(config)
gist_factory = Gist(image_factory, config)
db = ExhaustiveDb(config)

# To subsequently display the images, read all the file names from the
# directory where all the images in the database were originally found.
# !! Strong assumption: no changes, same names, same order...
image_list = sorted([f for f in os.listdir(images_dir) if f.endswith('.jpg')])
N = len(image_list)

# Clean the display thing, it is a bug in Linux.
def clean_display():
    for i in range(len(ImageShow._viewers)):
        if ImageShow._viewers[i].__class__.__name__ == 'XVViewer':
            del ImageShow._viewers[i]


import logging 
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__package__)
import os, sys, time
import random
 
import numpy as np
import scipy.sparse

from decoder.image import Imdec
from descriptor.gists import Gist
from indexation.exhaustive import ExhaustiveDb

#configuration

# Please insert here the correct paths where the images can be found.
# The VisualDatabase contains all the distracting images+the originales


results_dir = "./"
images_dir = "Copydays/VisualDatabase"
database_name = "VisualDatabase.h5"
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

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

#list of input images
image_list = sorted([f for f in os.listdir(images_dir) if f.endswith(".jpg")])
N = len(image_list)

#create the pipeline
image_factory = Imdec(config)
gist_factory = Gist(image_factory, config)
db = ExhaustiveDb(config)

#load the database or index the images
try:
    #Try loading an existing database 
    db.load()
    log.info("\n\n\nWarning---the database %s already exists\n\n" % db.dbfile)
except:
    #failure, probably not done the indexed yet
    log.info("Failed to load database, indexing.")
    for i, d in enumerate(gist_factory.getbyfilelist(image_list)):
        db.insert(d[0]['desc'], i)
        if i % 100 == 99:
            log.info("Indexed %d/%d" % (i+1, N))
    db.save()
    #saved for next time

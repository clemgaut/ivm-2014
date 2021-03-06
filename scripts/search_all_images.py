import logging 
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__package__)
import os, sys, time
import random
import Image
import ImageDraw
import ImageFont
import ImageShow
import numpy as np
import scipy.sparse

from decoder.image import Imdec
from descriptor.gists import Gist
from indexation.exhaustive import ExhaustiveDb

#configuration
results_dir = "./"
#images_dir = "/local/lamsaleg/IVM2/Copydays/VisualDatabase"
images_dir = "/home/clemgaut/Documents/Master/IVM/IVM2/Copydays/VisualDatabase"
#query_dir = "/local/lamsaleg/IVM2/Copydays/Queries"
query_dir = "/home/clemgaut/Documents/Master/IVM/IVM2/Copydays/Queries"
database_name = "VisualDatabase.h5"
# clean the display thing:
for i in range(len(ImageShow._viewers)):
    if ImageShow._viewers[i].__class__.__name__ == "XVViewer":
        del ImageShow._viewers[i]

config = { 
    'common': {
        'dir': results_dir,
    },
    'Imdec': {
        'basedir': images_dir,
    },
    'Gist': {
        'image_resize': (64, 64), 
        'power_law': None, 
        'normalization': "L2", 
    },
    'ExhaustiveDb': {
        'drop_zero': True, 
        'knn': 100, #number of nearest neighbors to retreive
        'disttype': "L2", 
        'dbfile': database_name,
    },
}

# to subsequently display the images, read all the file names from the
# directory where all the images in the database were originally found.
# !! strong assumption: no changes, same names, same order...
DBimage_list = sorted([f for f in os.listdir(images_dir) if f.endswith(".jpg")])
DB_N = len(DBimage_list)


Qimage_list = sorted([f for f in os.listdir(query_dir) if f.endswith(".jpg")])
Q_N = len(Qimage_list)


image_factory = Imdec(config)
gist_factory = Gist(image_factory, config)
db = ExhaustiveDb(config)
db.load()
# Create some matrix for the result. Each made of as many lines as there are query
# images, and as many columns as there are images in the database.
#
# sure, we could use fewer data structures but who cares?
resultsScores = np.zeros((Q_N, DB_N), dtype=np.float32) # will record a score
resultsDists = np.zeros((Q_N, DB_N), dtype=np.float32)  # will record distances. NO distances can be exactly 0 here.
resultsBinary = np.zeros((Q_N, DB_N), dtype=np.int)    # will record occurences


#loop on all the query images and for each, get its k NN
for qi_nb, query_image in enumerate(Qimage_list):
    d=list(gist_factory.getbyfile(query_dir+"/"+query_image))
    labels, dists = db.select(d[0]['desc'])
    resultsScores[qi_nb, labels] = 1. / (1. + dists)
    resultsDists[qi_nb, labels] = dists
    resultsBinary[qi_nb, labels] = 1

#provided results is initialised with ZEROs...
# np.count_nonzero(resultsDists[0])   :   this gives the # of NN found for the first image (should be 100)
# np.nonzero(resultsDists[0])   :   indices where these NN have been found
# resultsDists[0,np.nonzero(resultsDists[0])] : their score or distance...


#np.max(np.sum(resultsBinary,0)) : le nb de fois que l'image la + populaire apparait
#np.argmax(np.sum(resultsBinary,0)) : indice de la plus populaire
#DBimage_list[np.argmax(np.sum(resultsBinary,0))] son petit nom

# if you want to save the results to facilitate subsequent processing, here you go:
#np.save(os.path.join(results_dir, "resultsScores.npy"), resultsBinary)
np.save(os.path.join(results_dir, "resultsBinary.npy"), resultsBinary)
#np.save(os.path.join(results_dir, "resultsDists.npy"), resultsBinary)


#run scripts/search_all_images.py

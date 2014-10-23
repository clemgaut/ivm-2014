#!/usr/bin/python2

from config import *

clean_display()

Qimage_list = sorted([f for f in os.listdir(query_dir) if f.endswith('.jpg')])
Q_N = len(Qimage_list)

db.load()

# Create some matrix for the result. Each made of as many lines as there are query
# images, and as many columns as there are images in the database.
#
# Sure, we could use fewer data structures but who cares?
resultsScores = np.zeros((Q_N, N), dtype=np.float32) # will record a score
resultsDists = np.zeros((Q_N, N), dtype=np.float32) # will record distances. NO distances can be exactly 0 here.
resultsBinary = np.zeros((Q_N, N), dtype=np.int) # will record occurences

# Loop on all the query images and for each, get its k NN
for qi_nb, query_image in enumerate(Qimage_list):
    d = list(gist_factory.getbyfile(os.path.join(query_dir, query_image)))
    labels, dists = db.select(d[0]['desc'])
    resultsScores[qi_nb, labels] = 1. / (1. + dists)
    resultsDists[qi_nb, labels] = dists
    resultsBinary[qi_nb, labels] = 1

#provided result is initialised with ZEROs...
# np.count_nonzero(resultsDists[0])   :   this gives the # of NN found for the first image (should be 100)
# np.nonzero(resultsDists[0])   :   indices where these NN have been found
# resultsDists[0,np.nonzero(resultsDists[0])] : their score or distance...

#np.max(np.sum(resultsBinary,0)) : le nb de fois que l'image la + populaire apparait
#np.argmax(np.sum(resultsBinary,0)) : indice de la plus populaire
#DBimage_list[np.argmax(np.sum(resultsBinary,0))] son petit nom

# if you want to save the results to facilitate subsequent processing, here you go:
#np.save(os.path.join(results_dir, "resultsScores.npy"), resultsBinary)
#np.save(os.path.join(results_dir, "resultsBinary.npy"), resultsBinary)
#np.save(os.path.join(results_dir, "resultsDists.npy"), resultsBinary)


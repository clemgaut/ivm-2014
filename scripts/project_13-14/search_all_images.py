#!/usr/bin/python2
# -*- coding: utf-8 -*-

from config import *

import csv

def matrix2csv(m, file_name="default.csv"):
  
    f = open(file_name, "wb")
    c = csv.writer(f)
    
    for qi_nb in range(m.shape[0]):
	nn_tuple = np.nonzero(m[qi_nb])
	
	#nn_tuple is a tuple of array. To get all neigbours, get only the first value
	nn = nn_tuple[0]
	
	#Write the origin (qi_nb) and the destination (its NN)
	row = [qi_nb]
	row.extend(nn)
      
	c.writerow(row)
      
    f.close()

def snn(query_image, k):
        d = list(gist_factory.getbyfile(os.path.join(query_dir, query_image)))
        labels, dists = db.select(d[0]['desc'])
        knn_results = labels[0][:k]
        
        results = set(knn_results)
        
        #5eme idee: on cherche des images populaires
        #Parametre: taille de k, le nombre d'image populaire considere (a regler plus bas dans le code)
        #Le changement de ces parametres ameliore parfois la recherche des knn basique
        
        #On stock les distances des knns
        dist_knn = {}
        for i in range(0, len(labels[0])):
            dist_knn[labels[0][i]] = dists[0][i]
        
        results = set(knn_results[:k])
        snn_results = []
        
        #On initialise image_score qui contient le nombre de fois ou un knn apparait dans les snn.
        #image_id stocke les image considere par les images populaires
        image_id = {}
        image_score = {}
        for id in results:
            image_score[id] = 0
            image_id[id] = []
        
        for id in knn_results:
            #On calcul les knn des knn de l'image requete, on les appelle snn
            img_name = os.path.join(images_dir, image_list[id])
            e = list(gist_factory.getbyfile(img_name))
            labels_snn, dists_snn = db.select(e[0]['desc'])
            res = set([i for i in labels_snn[0][:k]])
            
            #On effectue l'interesection entre les knn et les snn
            l = results.intersection(res)
            
            #on memorise la distance des snn
            dist_snn = {}
            for i in range(0, len(labels_snn[0])):
                dist_snn[labels_snn[0][i]] = dists_snn[0][i]
            
            #Les knn present dans l'intersection font incrementer son score global 
            #On memorise la distance de l'image qui a fait augmenter ce score
            for i in l:
                image_score[i] += 1
                image_id[i].append((id, dist_snn[i]))
        
        #On pondere le score des knn par sa distance afin d'avantager les image tres semblable
        for id in results:
            image_score[id] /= dist_knn[id]
        
        #on tri les scores obtenues par les knn par ordre croissant
        #les images populaires sont celle qui ont le plus gros score et sont donc a la fin de la liste 
        popular_ids = []
        scores = image_score.values()
        scores.sort()
        #scores[-1] correspond au score le plus populaire, on peut baisser ce score en diminuant le -1
        #-1 permet de considerer uniquement l'image la plus populaire, -3 les 3 images les plus populaire, etc
        threshold = scores[-1]
        #On recupere les images qui ont un score plus eleve que le seuil choisis, ce sont nos images populaires
        max_ = max(image_score.values())
        for id, score in image_score.items():
            if score >= threshold:
                popular_ids.append(id)
                
        #On recupere les images considere par les images populaires
        for popular_id in popular_ids:
            for id_score in image_id[popular_id]:
                snn_results.append(id_score)
        
        #On enleve les image presente plusieurs fois, on ne garde que celle qui ont la meilleur distance
        snn_results.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        snn_results2 = []
        all_id = []
        for id, score in snn_results:
            if id in all_id: continue
            all_id.append(id)
            snn_results2.append((id, score))
        
        #On tri les meilleurs images en fonction de leur distance
        snn_results2.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        
        #On complete les resultats avec les knn non considerer par les images populaires
        used_id = []
        for id, score in snn_results2:
            used_id.append(id)
        final_result = list(snn_results2)
        for id in knn_results:
            if id in used_id: continue
            used_id.append(id)
            final_result.append((id, dist_knn[id]))
        
        #final_result.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        
        return [(id, score) for (id, score) in final_result]

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

resultsScoresSNN = np.zeros((Q_N, N), dtype=np.float32) # will record the score for SNN

#number of nearest shared neighbours
kSNN = 5

# Loop on all the query images and for each, get its k NN
for qi_nb, query_image in enumerate(Qimage_list):
    d = list(gist_factory.getbyfile(os.path.join(query_dir, query_image)))
    labels, dists = db.select(d[0]['desc'])
    resultsScores[qi_nb, labels] = 1. / (1. + dists)
    resultsDists[qi_nb, labels] = dists
    resultsBinary[qi_nb, labels] = 1
    
    #Compute SNN scores and store them
    score_list = snn(query_image, kSNN)
    
    labels = [[s[0] for s in score_list]]
    scores = [[s[1] for s in score_list]]
    
    resultsScoresSNN[qi_nb, labels] = scores
    
    
matrix2csv(resultsScoresSNN, "snn_neighbours.csv")


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


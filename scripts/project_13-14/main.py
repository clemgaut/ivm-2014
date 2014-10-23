#!/usr/bin/python
#-*- coding: utf-8

# Dependencies:
# python-gtk2
# glade-gtk2 (for editing 'main.glade')

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import math

# TODO:
# Modify 'config.py' so as to be able to modify the configuration dynamically
# (for SNN/KNN)
# Use module matplotlib to draw nice precision/recall plots, to display with
# Gtk!
# Use Gtk3 instead, much nicer!

# Code tips:
# Use 4 spaces instead of tabs for indenting (otherwise it will screw up with
# Python)
# If you want to try stuff, you can use the IPython interactive interpreter
# (much more practical than the default one)
# Use a real editor, like Vim :)

# Here you need the file 'config.py', and to have the right environment
# variables!
from config import *

# Maximum width and height of an image on the grid
MAX_WIDTH_IMG = 280
MAX_HEIGHT_IMG = 220
# Number of columns in the grid
COLS = 3

def resize_pixbuf(pixbuf, max_width=MAX_WIDTH_IMG, max_height=MAX_HEIGHT_IMG):
    width, height = pixbuf.get_width(), pixbuf.get_height()

    ratio = max(float(width) / max_width, float(height) / max_height)
    width = int(width / ratio)
    height = int(height / ratio)
    return pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)

class HelloWorld:
    def __init__(self):
        self.query_image = None
        # Open file containing the layout (edit with glade-gtk2)
        self.wTree = gtk.glade.XML('main.glade')
        # Whenever you want to access a widget from 'main.glade', do
        # self.wTree.get_widget
        self.window = self.wTree.get_widget('window')
        self.wTree.get_widget('query_image_chooser').set_current_folder(query_dir)
    
        # Useless for now, add a combobox to choose between K-NN of SNN
        search_methods = self.wTree.get_widget('search_methods')

        # Connect signals defined in main.glade
        dic = {'on_choose_file': self.on_choose_file, 'on_run': self.on_run}
        self.wTree.signal_autoconnect(dic)

        self.window.connect('destroy', gtk.main_quit)
        self.window.show_all()

    # Called when a file is chosen via the FileChooserWidget
    def on_choose_file(self, widget=None, data=None):
        self.query_image = widget.get_filename()
        self.update_query_image()
    # Called when an image is selected by clicking the link on the board
    def on_select_image(self, widget, text, data):
        self.query_image = data
        self.update_query_image()
       
    def update_query_image(self):
        image = self.wTree.get_widget('query_image')
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.query_image)
        image.set_from_pixbuf(resize_pixbuf(pixbuf, max_height=-1))
        #self.wTree.get_widget('query_image_name').set_text(os.path.split(self.query_image)[-1])

    # Called when "run" button is clicked (runs the query)
    def on_run(self, widget=None):
        #if self.query_image is None:
        #    return

        k = int(self.wTree.get_widget('k').get_value())
        use_knn = self.wTree.get_widget('knn_radiobutton').get_active()
        use_snn = self.wTree.get_widget('snn_radiobutton').get_active()
        
        d = None
        if use_knn:
            d = list(gist_factory.getbyfile(self.query_image))
            labels, dists = db.select(d[0]['desc'])
            results = [(labels[0][i], dists[0][i]) for i in range(len(labels[0]))]
        elif use_snn:
            results = self.snn(self.query_image, k)
            #result_size = 2
            #snn_result = [[0, 1], [1, 2]]
        
        result_panel = self.wTree.get_widget('result_panel')
        rows = int(math.ceil(k / COLS))
        result_table = gtk.Table(rows, COLS)

        for i, (id, score) in enumerate(results[:k]):
            img_name = os.path.join(images_dir, image_list[id]) # Full path
            #score = int(scores[i])
            
            # Open image, and resize it.
            pixbuf = gtk.gdk.pixbuf_new_from_file(img_name)
            image = gtk.Image()
            image.set_from_pixbuf(resize_pixbuf(pixbuf))
            
            label = gtk.Label()
            if use_snn:
                label.set_markup('<a href="run">#%d</a> <i>score=%f</i>' % (i+1, score))
            else:
                label.set_markup('<a href="run">#%d</a> <i>d=%f</i>' % (i+1, score))

            label.connect('activate-link', self.on_select_image, img_name)
            
            box = gtk.VBox()
            box.pack_start(image)
            box.pack_start(label)
            
            row = i / COLS
            col = i % COLS
            # Add the image to the table widget, at the right position
            result_table.attach(box, col, col + 1, row, row + 1, xpadding=10,
                    ypadding=10)
                        
        # Destroy (possibly) existing child before adding the new one to the
        # ViewPort
        child = result_panel.get_child()
        if child is not None:
            result_panel.remove(child)
        result_panel.add(result_table)
        result_panel.show_all()

    def snn(self, query, k):
        d = list(gist_factory.getbyfile(self.query_image))
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
        
        #On initialise image_score qui contient le nombre de fois où un knn apparait dans les snn.
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
        #les images populaires sont celle qui ont le plus gros score et sont donc à la fin de la liste 
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
        
        #2 eme idee multiplication 
        """ 
        l = results.intersection(res)
        if len(l) == 0: continue
        
        d = 1000
        for i in l:
            d *= dist[i]
            
        #d /= float(len(l))
        

        if d <= dist[list(results)[0]]*1000:
            snn_results.append((id, d))
        """  #Fin 2eme idee           
        
        #1ere idee, nb d'intersection
        """ 1ere idee avec le nb d'intersection
        for id in knn_results:
            img_name = os.path.join(images_dir, image_list[id])
            e = list(gist_factory.getbyfile(img_name))
            l, _ = db.select(e[0]['desc'])
            res = set([i for i in l[0][:k]])
            
            snn_results.append((id, len(results.intersection(res))))
        
        snn_results.sort(cmp=lambda x,y: cmp(y[1], x[1]))
        """ #Fin 1ere idee
        
        # 3eme idee, Utiliser la requete ou la 1ere image des knn_result comme image representative
        """
        list_snn = {}
        for id in results:
            img_name = os.path.join(images_dir, image_list[id])
            e = list(gist_factory.getbyfile(img_name))
            labels_snn, dists_snn = db.select(e[0]['desc'])
            res = set([i for i in labels_snn[0][:k]])
            list_snn[id] = res
        
        q_id = knn_results[0]
        
        knn_result2 = []
        for id in results:
            img_name = os.path.join(images_dir, image_list[id])
            e = list(gist_factory.getbyfile(img_name))
            labels_snn, dists_snn = db.select(e[0]['desc'])
            res = set([i for i in labels_snn[0][:k]])
            #res2= []
            
            #for q_id in res:
            #    res2.append(image_list[id])
            
            #query_id = 000000
            #print "HAAAAA", self.query_image
            #print res2
            if not(q_id in res): continue
            
            dist_snn = {}
            for i in range(0, len(labels_snn[0])):
                dist_snn[labels_snn[0][i]] = dists_snn[0][i]
                
            #l = results.intersection(res)
            #if len(l) < k/2: continue
            
            knn_result2.append((id, dist_snn[q_id]))
            
        """ #Fin 3eme idee
        
        # 4eme idee, on ne garde que les snn qui ont au moins un cardinal k/2 apres intersection avec les knn
        """
        knn_result2 = []
        for id in results:
            img_name = os.path.join(images_dir, image_list[id])
            e = list(gist_factory.getbyfile(img_name))
            labels_snn, dists_snn = db.select(e[0]['desc'])
            res = set([i for i in labels_snn[0][:k]])
            
            #dist_snn = {}
            #for i in range(0, len(labels_snn[0])):
            #    dist_snn[labels_snn[0][i]] = dists_snn[0][i]
                
            l = results.intersection(res)
            if len(l) < k/2: continue
            
            knn_result2.append(id)
                
            
            
            #print "KITTTTTY", knn_result2
            #print image_list[knn_result2[0]]

            #if len(l) < k/2: continue
            
            #knn_result2.append((id, len(l)))

        for id in list(knn_result2):
            for id2 in list(knn_result2):
                if id == id2: continue
                if not (id in list_snn[id2]):
                    try:
                        knn_result2.remove(id)
                    except: pass
        
        knn_result2.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        
        return [(id, score) for (id, score) in knn_result2]
        """ # fin 4eme idee
          
if __name__ == '__main__':
    hw = HelloWorld()
    db.load()
    gtk.main()


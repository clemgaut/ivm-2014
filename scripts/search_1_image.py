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
results_dir = "../results/"
#'/local/lamsaleg/IVM2/Copydays/VisualDatabase'
images_dir = "/home/clemgaut/Documents/Master/IVM/IVM2/Copydays/VisualDatabase"
database_name = "/home/clemgaut/Documents/Master/IVM/IVM2/VisualDatabase.h5"
#Clem modif
location_font = "/usr/share/fonts/truetype/ttf-dejavu/"


arg_list=sys.argv
print arg_list

# clean the display thing: it is a bug in Linux. If it crashes,
# then remove these lines...
for i in range(len(ImageShow._viewers)):
    if ImageShow._viewers[i].__class__.__name__ == "XVViewer":
        del ImageShow._viewers[i]

# the parameter that might matter for you is 'knn' below. This is the length
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

# to subsequently display the images, read all the file names from the
# directory where all the images in the database were originally found.
# !! strong assumption: no changes, same names, same order...
image_list = sorted([f for f in os.listdir(images_dir) if f.endswith(".jpg")])
N = len(image_list)

image_factory = Imdec(config)
gist_factory = Gist(image_factory, config)
db = ExhaustiveDb(config)

#loading an existing database 
db.load()

###########
# loop on all the queries given as argument; complete path with file name
for im_num,query_image in enumerate(arg_list[1:]):

    # compute the description of the query:
    log.info("\nComputing the description of the query %s\n" % query_image)
    d=list(gist_factory.getbyfile(query_image))
    
    # you want to see d? then uncomment the line below:
#    print d
    
# query with the vector part of the descriptor (ignore name, ...)
    labels, dists = db.select(d[0]['desc'])
    # want to see the identifiers of the 'k' most similar images as well as their
    # distances? Then uncomment next line
#    print labels, dists
    
    
# create an image where the query and the 10 most similar will be displayed
    s=250
    x=0
    y=5
    color=(255,255,255)
    #Clem modif
    #font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSansMono.ttf',12) #your fontpath might differ...
    font = ImageFont.truetype(location_font + 'DejaVuSansMono.ttf',12)
    
    result= Image.new("RGB", (1900, 1100), "grey")
    draw=ImageDraw.Draw(result)

            
#add the query image, left.
    im=Image.open(query_image)
    im.thumbnail((s,s))
    if im.size[0]<im.size[1]:
        im=im.rotate(90)
    result.paste(im, (0,150))
    draw.text( (0,350), 'Query Image', color, font=font)
    draw.text( (0,375), str(query_image.split("/")[-1:]), color, font=font)
        
# now loop on all the top 20 images
    x=s+10
    for i,id in enumerate(labels[0][:20]):
        img_name=images_dir + "/" +image_list[id]
    #    print img_name
        im=Image.open(img_name)
        if im.size[0]<im.size[1]:
            im=im.rotate(90)
        im.thumbnail((s,s), Image.ANTIALIAS)
        result.paste(im, (x,y))
        txt= "#"+str(i+1)+", d="+str(dists[0][i])
        draw.text( (x, y+185), txt, color, font=font)
        txt= "["+str(id)+"], "+ image_list[id]
        draw.text( (x, y+205), txt, color, font=font)
        x = x + s + 10
        if x > 1850-s:
            y = y + s + 10
            x = s + 10
    result.show()
    
    result.save(results_dir + 'res' + str(im_num) + '.png')
                    
#python scripts/search_1_image.py  /local/lamsaleg/IVM/Copydays/Queries/208?00.jpg


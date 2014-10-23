#!/usr/bin/python2

from config import *

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

# Load the database or index the images
try:
    # Try loading an existing database 
    db.load()
    log.info('\n\n\nWarning---the database %s already exists\n\n' % db.dbfile)

except:
    # Failure, probably not done the indexing yet
    log.info('Failed to load database, indexing.')
    
    for i, d in enumerate(gist_factory.getbyfilelist(image_list)):
        db.insert(d[0]['desc'], i)    
        if i % 100 == 99:
            log.info('Indexed %d/%d' % (i + 1, N))
    
    db.save()
    # Saved for next time


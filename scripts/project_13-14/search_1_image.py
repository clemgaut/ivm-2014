#!/usr/bin/python2

# Import variables from config.py
from config import *

# ./search_1_image.py xxxxxx.jpg

clean_display()

# Load an existing database 
db.load()

###########
# Loop on all the queries given as argument
for query_image in sys.argv[1:]:

    query_image = os.path.join(query_dir, query_image)
    # Compute the description of the query
    log.info('\nComputing the description of the query %s\n' % query_image)
    d = list(gist_factory.getbyfile(query_image))
    
    # Query with the vector part of the descriptor (ignore name, ...)
    labels, dists = db.select(d[0]['desc'])
    
    # Create an image where the query and the 10 most similar will be displayed
    s = 250
    x = 0
    y = 5
    color = (255, 255, 255)
    font = ImageFont.truetype(font_path, 12)
    
    result = Image.new('RGB', (1900, 1100), 'grey')
    draw = ImageDraw.Draw(result)

    # Add the query image, left.
    im = Image.open(query_image)
    im.thumbnail((s, s))
    
    if im.size[0] < im.size[1]:
        im = im.rotate(90)
    
    result.paste(im, (0, 150))
    draw.text((0, 350), 'Query Image', color, font=font)
    draw.text((0, 375), str(query_image.split('/')[-1:]), color, font=font)
        
    # Now loop on all the top 20 images
    x = s + 10
    for i, id in enumerate(labels[0][:20]):
        img_name = images_dir + "/" + image_list[id]
        im = Image.open(img_name)
        
        if im.size[0] < im.size[1]:
            im = im.rotate(90)

        im.thumbnail((s,s), Image.ANTIALIAS)
        result.paste(im, (x, y))
        txt = '#%d, d=%f' %  (i + 1, dists[0][i])
        draw.text((x, y + 185), txt, color, font=font)
        txt = '[%d], %s' % (id, image_list[id])
        draw.text((x, y + 205), txt, color, font=font)
        x = x + s + 10

        if x > 1850 - s:
            y = y + s + 10
            x = s + 10
    
    result.show()
                    

#As you know, google just a enginer, not an artist. The images that optimized are not good.

from google.appengine.api import images

def main(Entry, MimeType):
    img = images.Image(Entry)
    
    img.im_feeling_lucky()
    if (MimeType == 'image/x-png' or  MimeType == 'image/png'):
        encoding = images.PNG
    elif (MimeType == 'image/gif'):
        encoding = images.GIF
    else:
        encoding = images.JPEG
        
    thumbnail = img.execute_transforms(output_encoding = encoding)

    return thumbnail

# my_apps/image/templatetags/image_tags.py
import os.path

from django import template

FMT = 'JPEG'
EXT = 'jpg'
QUAL = 75

register = template.Library()


def resized_path(path, size, method):
    "Returns the path for the resized image."

    dir, name = os.path.split(path)
    image_name, ext = name.rsplit('.', 1)
    return os.path.join(dir, '%s_%s_%s.%s' % (image_name, method, size, EXT))


def scale(imagefield, size, method='scale'):
    """ 
    Template filter used to scale an image
    that will fit inside the defined area.

    Returns the url of the resized image.

    {% load image_tags %}
    {{ profile.picture|scale:"48x48" }}
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)

    image_path = resized_path(imagefield.path, size, method)

    if not os.path.exists(image_path):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        image = Image.open(imagefield.path)

        # normalize image mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # parse size string 'WIDTHxHEIGHT'
        width, height = [int(i) for i in size.split('x')]

        # use PIL methods to edit images
        if method == 'scale':
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(image_path, FMT, quality=QUAL)

        elif method == 'crop':
            try:
                import ImageOps
            except ImportError:
                from PIL import ImageOps

            ImageOps.fit(image, (width, height), Image.ANTIALIAS
                        ).save(image_path, FMT, quality=QUAL)

    return resized_path(imagefield.url, size, method)



def crop(imagefield, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    return scale(imagefield, size, 'crop')


register.filter('scale', scale)
register.filter('crop', crop)
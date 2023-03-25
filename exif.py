
import logging
from exif import Image

x = input()
f = open(x, 'rb')
file = Image(f)


images = [file]

for index, image in enumerate(images):
    if image.has_exif:
        status = f"contains EXIF (version {image.exif_version}) information."
    else:
        status = "does not contain any EXIF information."
    print(f"Image {index} {status}")

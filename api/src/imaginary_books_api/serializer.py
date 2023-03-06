import sys, os, io, fnmatch
from urllib.request import urlopen
import PIL.Image as Image

class LazyCallable(object):
    def __init__(self, name):
        self.n, self.f = name, None
    def __call__(self, *a, **k):
        if self.f is None:
            modn, funcn = self.n.rsplit('.', 1)
            if modn not in sys.modules:
                __import__(modn)

            self.f = getattr(sys.modules[modn],
                       funcn)
        self.f(*a, **k)

def _format(
    method: str,
    data,
):
    if method=='book_add':
        return book_add(data)

def book_add(datalist):
    ret = list()
    keys = datalist[0]
    for data in datalist[1:]:
        d = dict()
        for idx, key in enumerate(keys):
            assoc_data = data[idx]
            if key=='authors':
                d[key] = [x.strip() for x in assoc_data.split(',')]
            elif key=='genre':
                d['genres'] = [assoc_data]
            elif key=='pageCount':
                d[key] = int(assoc_data)
            elif key=='retailPrice':
                d['retail_price'] = float(assoc_data)
            elif key=='publishedDate':
                d[key] = int(assoc_data.split('/')[-1])
            elif key=='ISBN-10':
                d['isbn_10'] = assoc_data.strip()
            elif key=='ISBN-13':
                d['isbn_13'] = assoc_data.strip()
            elif key=='height' or key=='width' or key=='thickness':
                d[key] = centiToInches(assoc_data.strip())
            elif key=='cover':
                if assoc_data=='':
                    d['setDefaultImage'] = 'true'
                else:
                    if (image_filename := urlToFile(assoc_data, data[keys.index('ISBN-13')])) is not None:
                        d['image'] = image_filename
                        d['authors'] = ','.join(d['authors'])
                        d['genres'] = ','.join(d['genres'])
                    else:
                        d['setDefaultImage'] = 'true'
            else:
                d[key] = assoc_data.strip()
        ret.append(d)
    
    return ret


def find_pattern(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append({
                    "full_path": os.path.join(root,name),
                    "filename": name,
                })
    return result

def check_if_image_exists(
    filename,
):
    filename = filename.strip()
    download_abs_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'images'))
    regex=f'{filename}.*'
    filepath = find_pattern(regex, download_abs_path)
    return filepath[0].get('filename', None)

def urlToFile(
    end_url,
    isbn_13,
):
    if((image_filename := check_if_image_exists(isbn_13)) is not None):
        return image_filename

    try:
        resp = urlopen(end_url)
    except Exception as e:
        # Case where defualt image does not exist
        return None
    
    image_bytes= resp.read()

    image_filename = create_local_image(isbn_13, image_bytes)

    return image_filename


def create_local_image(filename_without_extension, image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        filename = f'{filename_without_extension.strip()}.{image.format.lower()}'
        download_abs_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'images'))
        absolute_location = f'{download_abs_path}/{filename}'
        image.save(absolute_location)
    except Exception as e:
        # This means that the image_bytes is corrupted revert to default image in this case
        print(e)
        return None

    return filename # Absolute location is used to send the static file to image server
    

def centiToInches(
    centi: str
) -> float:
    """Convert Google Books cm to Inches

    Args:
        centi: string formated as {size} cm

    Returns:
        inch: Converted cm value to inches in float format

    *Note
        Google Books gives us the size in cm(str) thus, conversion is needed

    """
    if centi == '':
        return float(0)

    # remove unit
    unit = 'cm'

    centi_reformatted = float(centi.replace(unit, "").strip())

    inch = '{0:.2f}'.format(centi_reformatted/2.54)
    return float(inch)
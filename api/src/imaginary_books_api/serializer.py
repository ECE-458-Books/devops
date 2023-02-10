import sys

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
            else:
                d[key] = assoc_data.strip()
        ret.append(d)
    
    return ret

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
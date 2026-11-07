import copy,math
from agreement import validate_response as validate_xywh

def validate_corners(data):
    if not isinstance(data,dict) or set(data)!={'completed','pictures'} or data['completed'] is not True or not isinstance(data['pictures'],list):raise ValueError('Complete corner annotation required')
    out=copy.deepcopy(data)
    for p in out['pictures']:
        b=p.get('box')
        if not isinstance(b,list) or len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b):raise ValueError('Four finite normalized corners required')
        l,t,r,bottom=b
        if not(0<=l<r<=1 and 0<=t<bottom<=1):raise ValueError('Invalid ordered corners; no repair')
        p['box']=[l,t,r-l,bottom-t]
    return validate_xywh(out)

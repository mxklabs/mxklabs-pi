import collections

#ArcParams = collections.namedtuple("ArcParams", ["centre", "radius",
#    "start_angle", "end_angle"])

import datetime

def utc_to_local(utc):
    return utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
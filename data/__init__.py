from .jcms import DRIVERS
from .g8fmap import JOINT_MAP as G8F_MAP
from .g8mmap import JOINT_MAP as G8M_MAP


def getJointMap(figure_name):

    joint_maps = {
        'Genesis8Female': G8F_MAP,
        'Genesis8Male': G8M_MAP
    }

    return joint_maps[figure_name]

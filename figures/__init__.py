from .g8f import FIGURES as G8F
from .g8m import FIGURES as G8M
from ..core import G8Mesh

FIGURE_MAP = {
    'g8f': G8F,
    'g8m': G8M
}


def loadMeshes(name):
    mesh_list = [G8Mesh(**figure_args)
                 for figure_args in FIGURE_MAP[name.lower()]]
    return mesh_list

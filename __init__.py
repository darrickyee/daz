import os
import sys
if not any(os.path.basename(p) for p in sys.path):
    sys.path.append(os.path.dirname(__file__))
from .skmapper import SkeletonMapper
from .main import execTransfer

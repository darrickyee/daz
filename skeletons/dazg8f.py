
JOINT_MAP = {'COG_M': 'hip',
             'Pelvis_M': 'pelvis',
             'Spine1_M': 'abdomenLower',
             'Spine2_M': 'abdomenUpper',
             'Spine3_M': 'chestLower',
             'Spine4_M': 'chestUpper',
             'Neck_M': 'neckLower',
             'Head_M': 'head',
             'HeadEnd_M': '',
             'Jaw_M': 'lowerJaw',
             'JawEnd_M': 'Chin',
             'Tongue1_M': 'tongue01',
             'Tongue2_M': 'tongue02',
             'Tongue3_M': 'tongue03',
             'Tongue4_M': 'tongue04',
             'TongueEnd_M': '',
             'Hip_R': 'rThighBend',
             'Knee_R': 'rShin',
             'Ankle_R': 'rFoot',
             'Toes_R': 'rToe',
             'ToesEnd_R': '',
             'Breast_R': 'rPectoral',
             'Clavicle_R': 'rCollar',
             'Shoulder_R': 'rShldrBend',
             'Elbow_R': 'rForearmBend',
             'Wrist_R': 'rHand',
             'FingerThumb1_R': 'rThumb1',
             'FingerThumb2_R': 'rThumb2',
             'FingerThumb3_R': 'rThumb3',
             'FingerThumbEnd_R': '',
             'FingerIndex1_R': 'rIndex1',
             'FingerIndex2_R': 'rIndex2',
             'FingerIndex3_R': 'rIndex3',
             'FingerIndexEnd_R': '',
             'FingerMiddle1_R': 'rMid1',
             'FingerMiddle2_R': 'rMid2',
             'FingerMiddle3_R': 'rMid3',
             'FingerMiddleEnd_R': '',
             'FingerRing1_R': 'rRing1',
             'FingerRing2_R': 'rRing2',
             'FingerRing3_R': 'rRing3',
             'FingerRingEnd_R': '',
             'FingerPinky1_R': 'rPinky1',
             'FingerPinky2_R': 'rPinky2',
             'FingerPinky3_R': 'rPinky3',
             'FingerPinkyEnd_R': '',
             'Eye_R': 'rEye',
             'EyeEnd_R': '',
             }

TWIST_JNTS = [
    'Shoulder_R',
    'Elbow_R',
    'Hip_R'
]

MANUAL_XFORMS = {
    'HeadEnd_M': (0, 20, 0),
    'BreastEnd_R': (-6.227, 4.643, 17.1455),
    'HeelEnd_R': (1, -7, -6),
    'ToesEnd_R': (-2, -1, 5),
    'ButtockEnd_R': (-7, -11, -13)
}


class SkeletonMap(object):

    def __init__(self):
        self.map = JOINT_MAP
        self.twist_joints = TWIST_JNTS
        self.manual_xforms = MANUAL_XFORMS

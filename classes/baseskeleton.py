
ORIENT_GRPS = [
    ['Clavicle_R', 'Shoulder_R', 'Elbow_R', 'Wrist_R'],
    ['Wrist_R', 'FingerMiddle1_R', 'FingerMiddle2_R', 'FingerMiddle3_R'],
    ['FingerThumb1_R', 'FingerThumb2_R', 'FingerThumb3_R'],
    ['FingerIndex1_R', 'FingerIndex2_R', 'FingerIndex3_R'],
    ['FingerRing1_R', 'FingerRing2_R', 'FingerRing3_R'],
    ['FingerPinky1_R', 'FingerPinky2_R', 'FingerPinky3_R'],
    ['Hip_R', 'Knee_R', 'Ankle_R', 'Toes_R'],
    ['Spine1_M', 'Spine2_M', 'Spine3_M', 'Spine4_M', 'Neck_M', 'Head_M'],
    ['Breast_R', 'BreastEnd_R'],
    ['Toes_R', 'ToesEnd_R'],
    ['Eye_R', 'EyeEnd_R'],
    ['Jaw_M', 'JawEnd_M'],
    ['Tongue1_M', 'Tongue2_M', 'Tongue3_M', 'Tongue4_M']
]

MANUAL_ORIENTS = {
    'Root_M': {},
    'COG_M': {'aim_offset': (0, 1, 0)},
    'Head_M': {'aim_offset': (0, 1, 0)},
    'Ankle_R': {'aim_offset': (0, -1, 0), 'up_obj_name': 'Toes_R', 'up_vector': (0, -1, 0)},
    'Eye_R': {'aim_offset': (0, 0, 1)}
}

TREE_R = {'Root_M': None,
          'COG_M': 'Root_M',
          'Pelvis_M': 'COG_M',
          # 'GensBase_M': 'Pelvis_M',
          'Spine1_M': 'COG_M',
          'Spine2_M': 'Spine1_M',
          'Spine3_M': 'Spine2_M',
          'Spine4_M': 'Spine3_M',
          'Neck_M': 'Spine4_M',
          'Head_M': 'Neck_M',
          'HeadEnd_M': 'Head_M',
          'Jaw_M': 'Head_M',
          'Tongue1_M': 'Jaw_M',
          'Tongue2_M': 'Tongue1_M',
          'Tongue3_M': 'Tongue2_M',
          'Tongue4_M': 'Tongue3_M',
          'TongueEnd_M': 'Tongue4_M',
          'JawEnd_M': 'Jaw_M',
          'ButtockEnd_R': 'Pelvis_M',
          'Hip_R': 'Pelvis_M',
          'Knee_R': 'Hip_R',
          'Ankle_R': 'Knee_R',
          'Toes_R': 'Ankle_R',
          'ToesEnd_R': 'Toes_R',
          'HeelEnd_R': 'Ankle_R',
          'Breast_R': 'Spine3_M',
          'BreastEnd_R': 'Breast_R',
          'Clavicle_R': 'Spine4_M',
          'Shoulder_R': 'Clavicle_R',
          'Elbow_R': 'Shoulder_R',
          'Wrist_R': 'Elbow_R',
          'FingerThumb1_R': 'Wrist_R',
          'FingerThumb2_R': 'FingerThumb1_R',
          'FingerThumb3_R': 'FingerThumb2_R',
          'FingerThumbEnd_R': 'FingerThumb3_R',
          'FingerIndex1_R': 'Wrist_R',
          'FingerIndex2_R': 'FingerIndex1_R',
          'FingerIndex3_R': 'FingerIndex2_R',
          'FingerIndexEnd_R': 'FingerIndex3_R',
          'FingerMiddle1_R': 'Wrist_R',
          'FingerMiddle2_R': 'FingerMiddle1_R',
          'FingerMiddle3_R': 'FingerMiddle2_R',
          'FingerMiddleEnd_R': 'FingerMiddle3_R',
          'FingerRing1_R': 'Wrist_R',
          'FingerRing2_R': 'FingerRing1_R',
          'FingerRing3_R': 'FingerRing2_R',
          'FingerRingEnd_R': 'FingerRing3_R',
          'FingerPinky1_R': 'Wrist_R',
          'FingerPinky2_R': 'FingerPinky1_R',
          'FingerPinky3_R': 'FingerPinky2_R',
          'FingerPinkyEnd_R': 'FingerPinky3_R',
          'Eye_R': 'Head_M',
          'EyeEnd_R': 'Eye_R', }


class BaseSkeleton(object):

    def __init__(self):

        self.joint_names = [jname for jname in TREE_R]
        self.joint_tree = TREE_R
        self.orient_grps = ORIENT_GRPS
        self.manual_orients = MANUAL_ORIENTS

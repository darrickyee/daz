HEAD_MAP = {'Neck_M': 'neckLower',
            'Head_M': 'head',
            'Jaw_M': 'lowerJaw',
            'JawEnd_M': 'Chin',
            'Tongue1_M': 'tongue01',
            'Tongue2_M': 'tongue02',
            'Tongue3_M': 'tongue03',
            'Tongue4_M': 'tongue04',
            'Eye_R': 'rEye',
            'Eye_L': 'lEye'
            }

for jnt in HEAD_MAP:
    sk_jnt = pm.ls(jnt)[0]
    tgt_jnt = pm.ls(HEAD_MAP[jnt])[0]

    pm.move(sk_jnt, tgt_jnt.getTranslation(space='world'), ws=True, pcp=True)

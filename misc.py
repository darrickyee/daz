import os

in_file = 'C:/Users/DSY/Documents/maya/projects/_UE4-Chars/scenes/Rig/dev_g8fpc2.ma'

with open(in_file, mode='r') as f:
    tmp_file = in_file+'_TMP'
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    with open(tmp_file, 'w') as tf:
        lines = (line for line in f if 'fileInfo "license" "student";' not in line)
        tf.writelines(lines)

    # os.remove(in_file)
    # os.rename(tmp_file, in_file)
import pymel.core as pm

def copyLocRot(xform, loc_node, rot_node):
    xform, loc_node, rot_node = (
        pm.ls(arg)[0] for arg in (xform, loc_node, rot_node))
    pm.delete(pm.pointConstraint(loc_node, xform))
    pm.delete(pm.orientConstraint(rot_node, xform))

copyLocRot(heelxf, rot_node='Ankle_R', loc_node='Toes_R')

matKnee = jnt.getMatrix(ws=True)
locAnkle = pm.ls('Ankle_R')[0].getTranslation(ws=True)

matKnee[-1] = list(locAnkle) + [1]
xf = pm.createNode('transform')
xf.setTransformation(matKnee)
heelxf = pm.createNode('transform')

heelvtx = pm.ls('BodyGeo:Mesh.vtx[7737]')[0]
heel_loc = heelvtx.getPosition()

heelxf.setParent(None)
heelxf.setTranslation(heel_loc)
heelxf.setParent(xf)
heelxf.setRotation((0, 0, 0))

heelxf.translateZ.set(0)
heelxf.setTranslation(heelxf.translate.get().normal()
                        * (heelxf.translate.get().length()+.5))

toevtx = pm.ls('BodyGeo:Mesh.vtx[8881]')[0]

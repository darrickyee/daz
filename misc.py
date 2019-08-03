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

# -*- coding: utf-8 -*-
# Install shelf button
# Execute it once to install and set the button on the Script Editor
#   import sys
#   sys.path.append("PATH/CannonThomasP2_MayaUtilityTool")
#   import installP02
#   installP02.install_Button()

import os
import maya.cmds as cmds

TOOL_FOLDER = r"C:\Users\Mili\Downloads\CannonThomasP2_MayaUtilityTool"
SCRIPT_FILE = os.path.join(TOOL_FOLDER, "CannonThomas_P02_code.py")
ICON_FILE = os.path.join(TOOL_FOLDER,"icon.png")

def install_Button():
    if not os.path.exists(SCRIPT_FILE):
        cmds.error("Could not find script file:\n{}".format(SCRIPT_FILE))
        return

    g_shelf_top = mel_eval("$tmpVar=$gShelfTopLevel")
    current_shelf = cmds.tabLayout(g_shelf_top, query=True, selectTab=True)
        
    command = f'''
import sys
import importlib

tool_path = r"{TOOL_FOLDER}"
if tool_path not in sys.path:
    sys.path.append(tool_path)

import CannonThomas_P02_code
importlib.reload(CannonThomas_P02_code)
CannonThomas_P02_code.show_window()
'''

    kwargs = {
        "parent": current_shelf,
        "label": "Maya Scatter Tool",
        "command": command,
        "annotation": "Maya Scatter Tool",
        "imageOverlayLabel": "Scatter Tool",
        "sourceType": "python",
    }

    if os.path.exists(ICON_FILE):
        kwargs["image1"] = ICON_FILE

    cmds.shelfButton(**kwargs)
    print("Maya Tool Installed.")
    print(ICON_FILE)

def mel_eval(command):
    import maya.mel as mel
    return mel.eval(command)

install_Button()

# -*- coding: utf-8 -*-
###############################################
#  "Artist-Directed Scatter Tool for Maya"  by Thomas Cannon
#  Features:
#  - 
#
# It can be called from the Script Editor 
#    import CannonThomas_P02_code
#    CannonThomas_P02_code.show()
###############################################
# Math Operations
import math  
# For random properties
import random
# Allow Python access to Maya commands. Create, move, rename, etc objects
import maya.cmds as cmds 
# Imports Maya's lower level User Interface (UI)
from maya import OpenMayaUI as omui 
#Shiboken is a bridge between Maya C++ Qt objects and Python Qt objects like buttons, labels, etc.
try:
    from shiboken2 import wrapInstance  
except ImportError:
    from shiboken6 import wrapInstance

#Qt core include timers,signals/slots,threading,event systems,base Qt functionality
try:
    from PySide2 import QtCore, QtWidgets
#    PYSIDE_VERSION = 2
except ImportError:
    from PySide6 import QtCore, QtWidgets
#    PYSIDE_VERSION = 6


WINDOW_OBJECT_NAME = "MayaTool"
WINDOW_TITLE = "Artist-Directed Scatter Tool for Maya"
ROOT_GROUP_NAME = "MayaTool_grp"


def maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    return None


def delete_if_exists(node):
    if node and cmds.objExists(node):
        cmds.delete(node)


def get_unique_name(base_name):
    if not cmds.objExists(base_name):
        return base_name

    index = 1
    while True:
        candidate = f"{base_name}{index}"
        if not cmds.objExists(candidate):
            return candidate
        index += 1


def ensure_root_group():
    if not cmds.objExists(ROOT_GROUP_NAME):
        return cmds.group(empty=True, name=ROOT_GROUP_NAME)
    return ROOT_GROUP_NAME


def rotate_point_for_plane(point, plane):
    x, y, z = point

    if plane == "XZ":
        return (x, y, z)
    if plane == "XY":
        return (x, z, y)
    if plane == "YZ":
        return (y, x, z)

    return (x, y, z)



    
def close_existing():
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == WINDOW_OBJECT_NAME:
            try:
                widget.close()
                widget.deleteLater()
            except Exception:
                pass


def show():
    close_existing()
    window = AssetGeneratorUI()
    window.show()
    return window
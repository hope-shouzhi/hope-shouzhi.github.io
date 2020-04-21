import os
import subprocess
import re
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

__author__ = 'shouzhi chen'
LOG_DEBUG= 3
LOG_INFO = 2
LOG_ERR = 1
__debug = LOG_INFO
__no_color = False

def  color_print(color, infos):
    if ("red" in color):
        print('\033[1;31;40m')
        print(infos)

    if ("green" in color):
        print('\033[1;32;40m')
        print(infos)
        
    if ("yellow" in color):
        print('\033[1;33;40m')
        print(infos)

    if ("blue" in color):
        print('\033[1;34;40m')
        print(infos)
    if ("puple" in color):
        print('\033[1;35;40m')
        print(infos)
    if ("no" in color):
        print(infos)
        return

    print('\033[0m')
    return


def debug(infos):
    if __no_color:
        color_print("no", infos)
        return
    if __debug >= LOG_DEBUG:
        color_print("yellow", infos)
    return

def info(infos):
    if __no_color:
        color_print("no", infos)
        return
    if __debug >= LOG_INFO:
        color_print("green", infos)
    return


def error(infos):
    if __no_color:
        color_print("no", infos)
        return
    if __debug >= LOG_ERR:
        color_print("red", infos)
    return


#device.startActivity(component=componentName)
#componentName = 'com.hujiang.cctalk/.MainActivity'

APK_INFO_DICT = {'package':['name', 'package', ]}

global 

def install_apk(dir):
    #setup device
    info("Connecting device ...")
    device = MonkeyRunner.waitForConnection()
    info("Connected device")

    for apk in os.listdir(dir):
        apk_path = os.path.join(dir, apk)
        info("installing %s" % apk_path)
        device.installPackage(apk_path)
        info("installing %s sunccessful" % apk_path)

    return


def main(dir):




if __name__ == "__main__":
    root_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    debug("root_path " + root_path)
    main(dir)
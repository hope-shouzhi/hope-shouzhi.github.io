import os
import subprocess
import re
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

LOG_DEBUG = 3
LOG_INFO = 2
LOG_ERR = 1
__debug = LOG_DEBUG
__no_color = False
__author__ = 'shouzhi chen'


def color_print(color, infos):
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

def adb_cmd(cmd):
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        ret = proc.wait()
        if ret == 0:
            return True
        else:
            return False
    except Exception as error:
        error("ERROR: %s failed" % cmd)
        return False

def get_permission_info(aapt_path, apk_path):
    CMD = '{} dump permissions {}'
    debug(''.join("APK PATH: ", apk_path))

    aapt_cmd = CMD.format(aapt_path, apk_path)
    debug("CMD: " + aapt_cmd)
    permission_info = []
    try:
        proc = subprocess.Popen(aapt_cmd, stdout=subprocess.PIPE, shell=True)
        ret = proc.wait()

        if ret == 0:
            lines = proc.stdout.read().decode()
            debug("result: " + lines)

            if len(lines):
                for line in lines:
                    line = str(line)
                    package = re.search('package:', line)
                    if package:
                        debug("package: " + line)
                        tmp = line.split(" ")
                        debug(tmp[1])
                        permission_info.append(tmp[1])

                    perm = re.search('uses-permission:', line)
                    if perm:
                        debug("perm: " + line)
                        tmp = line.split(" ")
                        debug(tmp[1])
                        permission_info.append(tmp[1])
                return permission_info

            else:
                raise Exception("error")

        else:
            raise Exception("error")

    except Exception as error:
        error("ERROR: get apk info failed")
        return


def get_apk_info(aapt_path, apk_path):
    CMD = '{} dump badging {} | findstr /c:launchable-activity /c:package'
    debug(''.join("APK PATH: ", apk_path))

    aapt_cmd = CMD.format(aapt_path, apk_path)
    debug("CMD: " + aapt_cmd)
    package_name = ''
    activity_name = ''
    try:
        proc = subprocess.Popen(aapt_cmd, stdout=subprocess.PIPE, shell=True)
        ret = proc.wait()

        if ret == 0:
            lines = proc.stdout.read().decode()
            debug("result: " + lines)

            if len(lines):
                for line in lines:
                    line = str(line)
                    package = re.search('package:', line)
                    if package:
                        debug("package: " + line)
                        tmp = line.split(" ")
                        debug(tmp[1][6:-1])
                        package_name = tmp[1][6:-1]

                    activity = re.search('launchable-activity:', line)
                    if activity:
                        debug("activity: " + line)
                        tmp = line.split(" ")
                        debug(tmp[1][6:-1])
                        activity_name = tmp[1][6:-1]
                return package_name, activity_name

            else:
                raise Exception("error")

        else:
            raise Exception("error")

    except Exception as error:
        error("ERROR: get apk info failed")
        return None, None


"""
#device.startActivity(component=componentName)
#componentName = 'com.hujiang.cctalk/.MainActivity'

#DICT = {'package' : ['name', 'package', 'component]}
"""


def install_apk(dir):
    # setup device
    info("Connecting device ...")
    adb_cmd("adb wait-for-device")
    info("Connected device")

    install_cmd = 'adb install {}'
    for apk in os.listdir(dir):
        apk_path = os.path.join(dir, apk)
        info("installing %s" % apk_path)
        install_cmd.format(apk_path)
        adb_cmd(install_cmd)
        info("installing %s sunccessful" % apk_path)

    return


def main(dir):
    pass


if __name__ == "__main__":
    root_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    debug("root_path " + root_path)

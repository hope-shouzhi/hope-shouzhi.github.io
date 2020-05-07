import os
import subprocess
import re
import sys
import random
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

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
    debug(cmd)
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
    #debug(''.join("APK PATH: ", apk_path))
    aapt_cmd = CMD.format(aapt_path, apk_path)
    debug("CMD: " + aapt_cmd)
    permission_info = []
    try:
        proc = subprocess.Popen(aapt_cmd, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()

        if len(stdout):
            lines = stdout.decode()
            debug("result: " + lines)

            if len(lines) > 0:
                for line in lines.splitlines():
                    line = str(line)
                    debug(line)
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
                        permission_info.append(tmp[1][6:-1])
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
    debug("APK PATH: " + apk_path)

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
                for line in lines.splitlines():
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
        debug("ERROR: get apk info failed")
        return None, None

def install_apk(dir):
    # setup device
    info("Connecting device ...")
    adb_cmd("adb wait-for-device")
    info("Connected device")

    for apk in os.listdir(dir):
        apk_path = os.path.join(dir, apk)
        info("installing %s" % apk_path)
        install_cmd = 'adb install -g %s' % apk_path
        adb_cmd(install_cmd)
        info("installing %s sunccessful" % apk_path)

    return

#
def start_apk(package, apks_info, secs):
    if len(apks_info):
        while True:    
            index = random.randint(0,(len(apks_info)-1))
            debug('index：' + str(index))
            item = apks_info.get(package[index], None)
            if item is not None:
                adb_cmd('adb shell am start -n %s/%s' % (item[0], item[2]))
                time.sleep(secs)
    else:
        error("NO apk info found!")
    return

def config_perm_xml(xml_file_path, perm_info):
    doc = ET.parse(xml_file_path)
    xml_root = doc.getroot()
    except_element = ET.SubElement(xml_root, "exception")
    except_element.attrib = {"package":"%s" % perm_info[0]}
    debug("package: " + perm_info[0])
    perm_info.remove(perm_info[0])
    except_element.text = '\n \t'
    for i in range(len(perm_info)):
        debug(perm_info[i])
        permision_element = ET.SubElement(except_element, "permission")
        permision_element.attrib = {"name":"%s" % perm_info[i], "fixed":"false"}
        permision_element.tail ='\n \t'
        #except_element.append(permision_element)
    
    except_element.tail = '\n'
    #xml_root.append(except_element)
    
    doc.write(xml_file_path)
    return

if __name__ == "__main__":
    root_path = os.getcwd()
    package_list_file ='package_list.csv'
    apks_info = {}
    package_list = []
    if os.path.exists(package_list_file):
        with open(package_list_file, 'r') as f:
            for line in f:
                line = str(line)
                debug(line)
                debug(len(list(line.strip('\n').split(','))))
                pack_name, apk_name, apk_main_actitivity, null = line.strip('\n').split(',')
                package_list.append(pack_name)
                debug(package_list)
                apk_info = []
                apk_info.append(pack_name)
                apk_info.append(apk_name)
                apk_info.append(apk_main_actitivity)
                apks_info.setdefault(pack_name, apk_info)
                debug(apks_info)

    else:
        debug("root_path " + root_path)
        aapt = 'aapt.exe'
        aapt_path = os.path.join(root_path, 'android_cmd_tools')
        aapt_path = os.path.join(aapt_path, 'build-tools')
        aapt_path = os.path.join(aapt_path, '29.0.3')
        aapt_path = os.path.join(aapt_path, aapt)

        info("aapt_path: " + aapt_path)
        apk_dir = os.path.join(root_path, "apk")
        if os.path.exists(apk_dir):
            for apk in  os.listdir(apk_dir):
                apk_path = os.path.join(apk_dir, apk)
                info("apk_path: " + apk_path)
                package_name, main_activity = get_apk_info(aapt_path, apk_path)
                if package_name is not None:
                    package_list.append(package_name)
                    apk_info = "apk info package name: {}, main activity: {}"
                    apk_info = apk_info.format(package_name, main_activity)
                    info(apk_info)
                    each_apk = []
                    each_apk.append(package_name)
                    each_apk.append(apk)
                    each_apk.append(main_activity)
                    apks_info.setdefault(package_name, each_apk)

            with open(package_list_file, 'a') as f:
                for pack in package_list:
                    item = 'package name: {}, pack info: {}'
                    item = item.format(pack, apks_info.get(pack, ''))
                    for tmp in apks_info.get(pack, ''):
                        f.write(tmp + ',')
                    f.write('\n')
                    info(item)

            install_apk(apk_dir)

        else:
            error("APK DIR IS NOT existed.")
    start_apk(package_list, apks_info, 5)


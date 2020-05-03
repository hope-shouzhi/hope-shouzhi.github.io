import os
import subprocess
import re
import xml.etree.ElementTree as ET
import sys

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

class CommentedTreeBuilder ():
    def __init__(self, html = 0, target = None):
        ET.XMLTreeBuilder.__init__(self, html, target)
        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(ET.Comment, {})
        self._target.data(data)
        self._target.end(ET.Comment)


def config_perm_xml(xml_file_path, perm_info):
    doc = ET.parse(xml_file_path, parser = CommentedTreeBuilder())
    xml_root = doc.getroot()
    except_element = ET.SubElement(xml_root, "exception")
    except_element.attrib = {"package":"%s" % perm_info[0]}
    debug("package:  " + perm_info.remove(perm_info[0]))
    except_element.text = '\n \t'
    for i in len(perm_info):
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
    root_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    debug("root_path " + root_path)
    root_path = os.getcwd()
    debug("root_path " + root_path)

    xml_file_name = 'permissions.xml'
    aapt = 'aapt.exe'
    aapt_path = os.path.join(root_path, 'android_cmd_tools')
    aapt_path = os.path.join(aapt_path, 'build-tools')
    aapt_path = os.path.join(aapt_path, '29.0.3')
    aapt_path = os.path.join(aapt_path, aapt)

    info("aapt_path: " + aapt_path)
    apk_dir = os.path.join(root_path, "apk")
    for apk in  os.listdir(apk_dir):
        apk_path = os.path.join(apk_dir, apk)
        package_name, main_activity = get_apk_info(aapt_path, apk_path)
        info('apk_info %s, %s' % package_name, main_activity)


    #xml_file_path = os.path.join(root_path, xml_file_name)
    #config_perm_xml(xml_file_path, perm_info)



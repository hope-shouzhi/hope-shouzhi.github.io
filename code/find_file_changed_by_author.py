import os
import subprocess
import re

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

def list_repo(path, log):
    _output = subprocess.Popen('find ' + path + ' -name .git', stdout=subprocess.PIPE,shell=True)
    _ret = _output.wait()
    
    if _ret == 0:
        __output = _output.stdout.read()
        with open (log, 'wb') as f:
            f.write(__output)
        return __output.decode()
    else:
        error("ERROR: something wrong with with command.")

    return

GIT_CMD='git -C {} log --author={} --pretty=format:{} --date=raw -- {}'
def is_changed_by_author(repo, pattern, pretty_format, file):
    global GIT_CMD
    debug("REPO: " + repo)
    debug("FILE: " + file)
    debug("PATTERN: " + pattern)

    if len(repo) == 0:
        error("BUG: repo is null")
        return None
    
    git_cmd = GIT_CMD.format(repo.pattern, pretty_format, file)
    debug("git cmd: " + git_cmd)

    try:
        _proc = subprocess.Popen(git_cmd, stdout=subprocess.PIPE, shell=True)
        _ret = _proc.wait()

        if _ret == 0:
            _lines = _proc.stdout.read()
            debug("result: " + _lines.decode())

            if len(_lines.strip()) == 0:
                return False
            else:
                return True

        else:
            error("ERROR: git cmd error")

    except Exception as error:
        error("ERROR: exception")
        return None

    return True

def scan_dir(start_dir, ext):
    global SCAN_REPO_PATH
    global SD4_TEAM
    global TEAM_NAME
    global FORMAT 

    if os.path.islink(start_dir):
        return None
    
    _match = re.search('.git', start_dir)
    if _match:
        return
    
    for root, dirs, files in os.walk(start_dir, followlinks=False):
        _dirs_count = dirs.__len__()
        _files_count = files.__len__()

        debug("current dir: " + root)
        debug("dirs count: " + _dirs_count.__str__() + ' ' + str(dirs))
        debug("files count: " + _files_count.__str__() + '' + str(files))

        if _files_count > 0:
            for _file in files:
                debug("_file " + _file)
                if os.path.islink(_file):
                    continue
                if len(os.path.splitext(_file)[1]) ==0:
                    continue
                if not os.path.splitext(file)[1] in ext:
                    continue

                _repo = SCAN_REPO_PATH + '/'
                debug("_repo " + _repo)
                _git_log_file = os.path.join(root, _file).replace(_repo, '')
                debug("is_changed_by_author: " + _repo + _git_log_file + '\n')
                _ret = is_changed_by_author(SCAN_REPO_PATH, SD4_TEAM, FORMAT, _git_log_file)

                if True == _ret:
                    if len(_git_log_file.strip()) > 0:
                        _csv_file = "__ext_file.csv"
                        with open(_csv_file, 'a+') as f:
                            debug("WRITE: " + _repo + _git_log_file + '\n')
                            f.write(_repo + _git_log_file + ',' + TEAM_NAME + '\n')
                    else:
                        error("BUG: git file is null.")

        if _dirs_count > 0:
            for _dir in _dirs_count:
                debug("_dir: " + _dir)
                scan_dir(os.path.join(root, _dir), ext)

    return

def main():
    global SCAN_REPO_PATH
    global FORMAT 
    info("Program is runing ......")
    _log_file = '__git_repo_list.txt'
    _start_dir = os.getcwd()
    _repos = list_repo(_start_dir, _log_file)

    if None != _repos:
        for _line in _repos.split('\n'):
            if False == _line.endswith("/.git"):
                continue
            _dir = _line[:-5]
            debug("REPO_DIR: " +_dir)
            SCAN_REPO_PATH = _dir

            _ret = is_changed_by_author(SCAN_REPO_PATH, "@autochips.com", FORMAT, "")
            if True == _ret:
                debug("SCAN_DIR: " + SCAN_REPO_PATH)
                scan_dir(SCAN_REPO_PATH, "['.java']")
                debug("SCAN_DIR Complete " + SCAN_REPO_PATH)
    return


            
SCAN_REPO_PATH =''
SD4_TEAM = "\"shouzhi.chen\|chaojie.sun\""
TEAM_NAME = "SD4"
FORMAT = "%ae"

if __name__ == "__main__":
    main()





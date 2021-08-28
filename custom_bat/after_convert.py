# coding=utf-8

import sys
import os
import traceback
import shutil
import subprocess
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger(__name__)

def setlog(name, loglevel, log_dir="", log_rotate=31):
    # ログフォーマット
    log_format = logging.Formatter('%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s')

    # ログ設定
    main_logging = logging.getLogger(name)

    main_logging.setLevel(loglevel)

    # ログのコンソール出力
    sh = logging.StreamHandler()
    sh.setLevel(loglevel)
    sh.setFormatter(log_format)
    main_logging.addHandler(sh)

    # ログのファイル出力
    if log_dir != "":
        logfile = os.path.join(log_dir, 'after_convert.log')
    else:
        logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'after_convert.log')
    fh = TimedRotatingFileHandler(logfile, when="MIDNIGHT", backupCount=log_rotate)
    fh.setLevel(loglevel)
    fh.setFormatter(log_format)
    main_logging.addHandler(fh)

parser = argparse.ArgumentParser()
parser.add_argument('filepath')
parser.add_argument('--notanime', action='store_true', help='アニメ以外を処理する場合に指定')

if __name__ == "__main__":
    # ログ設定
    setlog(__name__, logging.DEBUG)

    try:
        logger.info("Start")

        args = parser.parse_args()
        logger.debug(args.filepath)
        logger.debug(args.notanime)

        filepath = args.filepath
        notanime = args.notanime

        filename = os.path.basename(filepath)
        filedir = os.path.dirname(filepath)
        newdir = "H:\\anime\\current"  # アニメの移動先
        if notanime:
            newdir = "H:\\ビデオ\\その他"  # アニメ以外の移動先
            logger.info("not anime")

        # pattern rename
        logger.info("Rename file")
        with open("E:\\Amatsukaze\\bat\\rename_list.txt") as f:
            lines = [s.strip() for s in f.readlines()]
        for line in lines:
            logger.debug(line)
            pattern = line.split(',')
            filename = filename.replace(pattern[0], pattern[1])
        rename = os.path.join(filedir, filename)
        os.rename(filepath, rename)
        filepath = rename

        if not notanime:
            # SCRename
            cmd = 'cscript //nologo E:\\Amatsukaze\\SCRename\\SCRename.vbs "' + filepath + '" "$SCtitle$_____$SCtitle$ 第$SCnumber2$話 「$SCsubtitle$」"'
            logger.debug(cmd)
            proc = subprocess.run(cmd, stdout = subprocess.PIPE, shell=True, cwd=filedir)
            filepath = proc.stdout.decode("cp932")[:-2]
            logger.debug(filepath)

        # move dir
        logger.info("Move file")
        newname = os.path.basename(filepath)
        logger.debug(newname)
        splitname = newname.split("_____")
        logger.debug(splitname)
        if len(splitname) > 1:
            newdir = os.path.join(newdir, splitname[0])
            if not os.path.isdir(newdir):
                os.makedirs(newdir)
            newname = splitname[1]
        logger.debug(newname)
        logger.debug(newdir)
        shutil.move(filepath, os.path.join(newdir, newname))

        logger.info("Complete")
    except:
        logger.error(traceback.format_exc())

#-*- coding:utf-8 -*-
#!/usr/bin/python

import os
import sys
import argparse

import subprocess, shlex



def prepare_directory(directory):
    """Convertit les images d'un répertoire en tif et fait l'ocr dessus"""
    print "Prépare le répertoire %s" % directory
     #1 Appeler mogrify pour convertir les png en tif
    cmd_mogrify = "mogrify -format tif %s/*.png" % directory
    args_mogrify = shlex.split(cmd_mogrify)
    p = subprocess.call(args_mogrify)

    walker = os.walk(directory)
    for w in walker:
        root, dirs, files = w
        for _dir in dirs:
            #Traite récursivement les sous-répertoires
            prepare_directory(_dir)
        for fichier in files:
            filename, file_ext = os.path.splitext(fichier)
            if file_ext == '.tif':
                tess_line = "/usr/bin/tesseract %s/%s %s/%s -l fra" % (os.getcwd(), fichier, os.getcwd(), filename)
                tess_box = "%s makebox" % tess_line
                args = shlex.split(tess_line)
                args2 = shlex.split(tess_box)
                p = subprocess.call(args)
                p = subprocess.call(args2)
             
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Numérise un ensemble d'images")
    parser.add_argument('--format', nargs=1)
    parser.parse_args(sys.argv)
"""    try:
        directory = sys.argv[1]
    except IndexError:
        directory = '.'

     #1 Appeler mogrify pour convertir les png en tif
    
    cmd_mogrify = "mogrify -format tif %s/*.png" % directory
    print cmd_mogrify
    args_mogrify = shlex.split(cmd_mogrify)
    p = subprocess.call(args_mogrify)

    #2 Appeler ocropus p-seg. pour fair eles zones
    cmd_opseg = "ocropus-pseg *.tif"
    print cmd_opseg
    args_opseg = shlex.split(cmd_opseg)
    p = subprocess.call(args_opseg)


    #3 pour chacun des répertoires
    prepare_directory(directory)
    #faire tesseract
    for f in os.listdir(directory):
        filename, file_ext = os.path.splitext(f)
        if file_ext == '.tif':
            cmd_hocr = "ocropus-hocr %s" % f
            args_hocr = shlex.split(cmd_hocr)
            p = subprocess.call(args_hocr)
"""

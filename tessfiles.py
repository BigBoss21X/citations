#-*- coding:utf-8 -*-
#!/usr/bin/python

import os
import sys
import argparse
import logging
import subprocess, shlex
from datetime import datetime

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
            prepare_directory("%s/%s" % (directory, _dir))
        for fichier in files:
            filename, file_ext = os.path.splitext(fichier)
            if file_ext == '.tif':
                tess_line = '/usr/bin/tesseract "%s/%s" "%s/%s" -l fra' % (directory, fichier, directory, filename)
                tess_box = "%s makebox" % tess_line
                print tess_line
                args = shlex.split(tess_line)
                args2 = shlex.split(tess_box)
                p = subprocess.call(args, stdout=subprocess.PIPE)
                p = subprocess.call(args2, stdout=subprocess.PIPE)
             
if __name__ == '__main__':
    #Configure le logger
    now = datetime.now()
    filename = "tessfiles-%02d%02d%02d-%02d%02d%02d.log" % (now.day, now.month, now.year, now.hour, now.minute, now.second)

    logging.basicConfig(filename=filename)
    parser = argparse.ArgumentParser(description="Numérise un ensemble d'images")
    parser.add_argument('--conversion-tif', action='store_true',
        help="Convertit les images contenues dans les répertoires en format tif")
    parser.add_argument('racine')
    parametres = parser.parse_args(sys.argv[1:len(sys.argv)])
  
    ## Fichiers initialement présents dans la racine.
    fichiers_racine = [f for f in os.listdir(parametres.racine)]
 
    #1 Appeler mogrify pour convertir les png en tif
    if parametres.conversion_tif:
        cmd_mogrify = "mogrify -format tif %s/*.png" % parametres.racine
        print cmd_mogrify
        args_mogrify = shlex.split(cmd_mogrify)
        print args_mogrify
        p = subprocess.call(args_mogrify)

    
    #2 Appeler ocropus p-seg. pour faire les zones
    for f in fichiers_racine:
        filename, file_ext = os.path.splitext(f) 
        cmd_opseg = "ocropus-pseg %s/%s%s" % (parametres.racine, filename, ".tif")
        print cmd_opseg
        args_opseg = shlex.split(cmd_opseg)
        p = subprocess.call(args_opseg, stdout=subprocess.PIPE)


    #3 pour chacun des répertoires
    prepare_directory(parametres.racine)
    #faire tesseract
    for f in fichiers_racine:
        filename, file_ext = os.path.splitext(f)
        cmd_hocr = "ocropus-hocr %s > %s" % (f, "%s.html" % filename)
        args_hocr = shlex.split(cmd_hocr)
        print cmd_hocr
        p = subprocess.call(args_hocr, stdout=subprocess.PIPE)
        print "ocr fait!"


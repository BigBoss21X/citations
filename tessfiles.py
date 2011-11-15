#-*- coding:utf-8 -*-
#!/usr/bin/python

import os
import sys
import argparse
import logging
import subprocess, shlex
import shutil
from datetime import datetime

from document import modele

if __name__ == '__main__':
    #Configure le logger
    now = datetime.now()
    filename = "tessfiles-%02d%02d%02d-%02d%02d%02d.log" % (now.day, now.month, now.year, now.hour, now.minute, now.second)
    logging.basicConfig(filename=filename)
    parser = argparse.ArgumentParser(description="Numérise un ensemble d'images")
    parser.add_argument('--conversion-tif', action='store_true',
        help="Convertit les images contenues dans les répertoires en format tif")
    parser.add_argument('--initialiser_repertoire', action='store',
        help="Crée les fichiers tesseract et boxfiles à partir des images d'un répertoire")
    parser.add_argument('--racine-document', action='store',
        help="Crée le document résidant à la racine")
    parser.add_argument('--creer-html', action='store_true',
        help='Crée le document HTML correspondant')

    parametres = parser.parse_args(sys.argv[1:len(sys.argv)])

    if parametres.racine_document:
        print "Initialisation du document"
        d = modele.Document(parametres.racine_document)
        if parametres.creer_html:
            d.as_html()
            try:
                os.mkdir("%s/css" % parametres.racine_document)
            except OSError, e:
                """Le dossier existe"""
                pass
            shutil.copy('document/templates/page.css', "%s/css" % parametres.racine_document)

    if parametres.initialiser_repertoire:
        ## Fichiers initialement présents dans la racine.
        fichiers_racine = [f for f in os.listdir(parametres.initialiser_repertoire)]

        tess_line = '/usr/bin/tesseract "%s/%s.tif" "%s/%s" -l fra'
        tess_box = "%s makebox" % tess_line

        commandes = [(tess_line % (parametres.initialiser_repertoire, os.path.splitext(f)[0], parametres.initialiser_repertoire, os.path.splitext(f)[0]),
                      tess_box % (parametres.initialiser_repertoire, os.path.splitext(f)[0], parametres.initialiser_repertoire, os.path.splitext(f)[0]))
                     for f in os.listdir(parametres.initialiser_repertoire)]

        #1 Appeler mogrify pour convertir les png en tif
        if parametres.conversion_tif:
            cmd_mogrify = "mogrify -format tif %s/*.png" % parametres.initialiser_repertoire
            print cmd_mogrify
            args_mogrify = shlex.split(cmd_mogrify)
            print args_mogrify
            p = subprocess.call(args_mogrify)
    
        for tess_cmd, box_cmd in commandes:
            subprocess.call(shlex.split(tess_cmd))
            subprocess.call(shlex.split(box_cmd))

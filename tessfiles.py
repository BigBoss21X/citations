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
    filename = "log/session-%02d%02d%02d-%02d%02d%02d.log" \
            % (now.day, now.month, now.year, now.hour, now.minute, now.second)
    logging.basicConfig(filename=filename, level=logging.DEBUG)

    parser = argparse.ArgumentParser(description=\
                                        "Numérise un ensemble d'images")
    parser.add_argument('--conversion-tif', action='store_true',
      help="Convertit les images contenues dans les répertoires en format tif")
    parser.add_argument('--initialiser_repertoire', action='store',
      help="Crée les fichiers tesseract et boxfiles à partir des \
images d'un répertoire")
    parser.add_argument('--creer-correctif', action='store_true',
        help="Crée les fichiers de correctifs")
    parser.add_argument('--racine-document', action='store',
        help="Crée le document résidant à la racine")
    parser.add_argument('--creer-html', action='store_true',
        help='Crée le document HTML correspondant')

    parametres = parser.parse_args(sys.argv[1:len(sys.argv)])

    if parametres.creer_correctif:
        if not parametres.racine_document:
            print "Vous devez spécifier la racine du document pour pouvoir\
 créer le fichier de correctif"
            sys.exit(1)
        logging.info("Création du correctif")
        racine = parametres.racine_document
        fichiers = sorted(set([os.path.splitext(f)[0] for f in os.listdir(racine)]))
        with open('%s/correctif.ini' % racine, 'w') as f:
            for fichier in fichiers:
                f.write(modele.template_correctif % ("%s%s" %(racine, fichier),'',''))
        print "création du correctif"

    if parametres.racine_document:
        print "Initialisation du document"
        logging.info("Initialisation du document")
        d = modele.Document(parametres.racine_document)
        #d.debug()
        d.output_resultats()
        if parametres.creer_html:
            d.as_html()
            try:
                os.mkdir("%s/css" % parametres.racine_document)
            except OSError, e:
                """Le dossier existe"""
                logging.warn("Le dossier [%s] existe" %\
                        parametres.racine_document)
            shutil.copy('document/templates/page.css',\
                    "%s/css" % parametres.racine_document)

    if parametres.initialiser_repertoire:
        repertoire = parametres.initialiser_repertoire
        logging.info("Initialisation du répertoire %s" % repertoire)
        ## Fichiers initialement présents dans la racine.
        fichiers_racine = [f for f in os.listdir(repertoire)]

        tess_line = '/usr/bin/tesseract "%s/%s.tif" "%s/%s" -l fra'
        tess_box = "%s makebox" % tess_line

        #Crée une liste de tuples contenant, pour chacun des fichiers du
        #répertoire, la commande tesseract pour numériser et la commandes
        #tesseract pour créer le boxfile.
        commandes = [(tess_line % (repertoire, os.path.splitext(f)[0],
                                   repertoire, os.path.splitext(f)[0]),
                      tess_box % (repertoire, os.path.splitext(f)[0],
                                  repertoire, os.path.splitext(f)[0]))
                                     for f in os.listdir(repertoire)]

        #Les fichiers numérisés sont souvent en format png, mais tesseract
        #exige le format tif
        if parametres.conversion_tif:
            cmd_mogrify = "mogrify -format tif %s/*.png" % parametres.initialiser_repertoire
            logging.info(cmd_mogrify)
            print cmd_mogrify
            args_mogrify = shlex.split(cmd_mogrify)
            print args_mogrify
            p = subprocess.call(args_mogrify)
    
        for tess_cmd, box_cmd in commandes:
            logging.info(tess_cmd)
            subprocess.call(shlex.split(tess_cmd))
            logging.info(box_cmd)
            subprocess.call(shlex.split(box_cmd))

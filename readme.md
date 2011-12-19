Glossaire
=========
* Répertoire source: répertoire dans lequel se trouvent les images à numériser.

Installation
============
À un moment où un autre le projet utilise les dépendances suivantes:

Général
-------
* tesseract 3, pour l'OCR.
* imagemagick, pour la conversion des images en format TIF (pour tesseract)

Il devrait être possible de les installer en utilisant le gestionnaire de paquets de votre distribution.


Python
------
* jinja2, la librairie utilisée pour convertir les documents en HTML.
* numpy, la librairie de calcul.
* BeautifulSoup, le parser de xml qui est utilisé pour lire les résultats.

Il est conseillé d'installer ces librairies dans un environnement virtuel python.

    # virtualenv env --no-site-packages

Pip est ensuite utilisé pour installer les librairies.

    # pip install jinja2
    # pip install numpy
    # pip install BeautifulSoup

Ruby
----
Les citations sont analysées et converties en format BibTeX par le logiciel anystyle-parser.
* anystyle-parser
* latex-decode
* wapiti-ruby

Pour avoir les dernières versions, celles-ci peuvent être clonées depuis github:

Dans le répertoire de votre choix:

    # git clone https://github.com/inukshuk/anystyle-parser.git
    # git clone https://github.com/inukshuk/latex-decode.git
    # git clone https://github.com/inukshuk/wapiti-ruby.git

Elles peuvent ensuite êtres installées en invoquant de la manière suivante. Par exemple, pour anystyle-parser:

    # gem build anystyle-parser.gemspec

Le gem résultant peut ensuite être installé:

    # sudo gem install anystyle-parser-0.0.8.gem

Utilisation
===========
:
Si vous utilisez un environnement virtuel, vous devez l'activer au préalable. Si vous l'avez appellé "env",
vous pouvez l'activer comme suit:

    # . env/bin/activate

Initialiser un répertoire
-------------------------
Initialiser le répertoire consiste à exécuter tesseract pour produire les fichiers texte et les boxfiles à partir de toutes les images présentes dans le répertoire racine.

    # python citations.py --initialiser-répertoire /chemin/vers/répertoire/racine

Les fichiers box et txt seront créés dans la répertoire spécifié. Les fichiers présents dans le répertoire racine doivent être en format tif. Si jamais il sont en format png peut être faite par le script:

    # python citations.py --initialiser-repertoire /chemin/vers/répertoire/racine --conversion-tif

Si les fichiers sont dans un autre format, elle devra être faite «manuellement»
    
    $ mogrify -format tif /chemin/vers/répertoire/racine/*.png

Analyser les fichiers produits par tesseract
--------------------------------------------
L'analyse de répertoire est l'action par défaut qui est faite par le script. Un seul paramètre est requis: la racine du document

    $ python citations.py --racine-document /chemin/vers/répertoire

Créer un correctif
------------------
Pour comparer les résultats obtenus par l'évaluateur d'appel, il faut d'abord créer un correctif:

    $ python citations.py --racine-document /chemin/vers/répertoire --creer-correctif

Un fichier nommé correctif.xml sera créé dans le répertoire. Un appel est présent par page. Cette balise peut être enlevée ou dupliquée dépendemment du nombre d'appel dans la page.

Comparer les résultats obtenus à ceux du correctif
--------------------------------------------------
Une fois le correctif complété, on souhaitera évaluer les résultats obtenus:

    $ python citations.py --comparaison-resultats /chemin/vers/correctif.xml /chemin/vers/resultats.xml /chemin/vers/comparatif.xml

Où:
* correctif.xml est le fichier correctif créé manuellement
* resultats.xml contient les résultats de l'évaluateur d'appels de notes de bas de page
* comparatif.xml sera créé et contiendra les résultats de comparaison.

L'ordre des fichiers est important: les citations manquantes ou superflues seront évaluées en fonction du premier fichier. Si les fichiers sont inversés, les résultats seront aussi inversés.

Extraire les références
-----------------------
Le module d'extraction de références peut être testé de la manière suivante:

    $ python bibliographie/bibliographie.py /chemin/vers/fichier/BibTeX

Un fichier BibTeX de test est fourni et est disponible à:

    $ python bibliographie/bibliographie.py bibliographie/biblio.bib

Étiquettage des ressources bibliographiques
-------------------------------------------
Un lanceur pour la librairie anystyle-wrapper a été écrit en ruby. Il peut être lancé avec la commande suivante:

    $ ruby lib/anystyle-wrapper.rb "référence"

Où référence est une référence bibliographique extraite du texte.

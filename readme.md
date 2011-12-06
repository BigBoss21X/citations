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

Si vous utilisez un environnement virtuel, vous devez l'activer au préalable. Si vous l'avez appellé "env",
vous pouvez l'activer comme suit:

    # . env/bin/activate

Initialiser un répertoire
-------------------------

Analyser les fichiers produits par tesseract
--------------------------------------------

Créer un correctif
------------------

Comparer les résultats obtenus à ceux du correctif
--------------------------------------------------

Extraire les références
-----------------------

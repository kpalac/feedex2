#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  Author: Karol Pałac (palac.karol@gmail.com)



"""
Sample language model (French) for developers
Change model data and run the script to generate header file, and then copy it to language models dir

"""

import pickle 
import snowballstemmer





# Modify data in the dictionary below
model = {
# List of possible names (e.g. if given in feed's meta info. First name on this list is a model name, so they need to be unique
# First item on the list is used as a model name in SmallSem
'names' : ('fr','FR','fr-*','Fr-*','FR-*', 'fra', 'FRA', 'french', 'French', 'FRENCH', 'fre', 'Français', 'FRE',),

# Stemmer and pyphen modules
'stemmer' : 'french', #Must be in snowballstemmer language list or None for no stemming
'pyphen' : 'fr',


# This data is useful for language detection
'alphabet' : 'abcdefghijklmnopqrstuvwxyz€ÀÂÄÈÉÊËÎÏÔŒÙÛÜŸàâäèéêëîïôœùûüÿÇç',
'numerals' : '1234567890',
'capitals' : 'ABCDEFGHIJKLMNOPRSTUVWXYZÇç', # This is useful to detect capitalized items but not essential
'vowels' : 'aeiouyÀÂÄÈÉÊËÎÏÔŒÙÛÜŸàâäèéêëîïôœùûüÿ€',
'consonants' : 'bcdfghjklmnpqrstvwxzÇç',
'unique_chars' : 'ÀÂÄÈÉÊËÎÏÔŒÙÛÜŸàâäèéêëîïôœùûüÿ€Çç',
'charsets' : ('iso-8859-1', 'windows-1252',),

# Linguistic info
'writing_system' : 1, # 1 - alphabetic, 2 - logographic
'bicameral' : 1, # is language 'case-sensitive'?
'name_cap' : 1, # 1 - names capitalized, 2 - all nouns capitalized (e.g. German), 0 - no capitals (non-bicameral)

# Tokenizer
# It is advised to include patterns for emails, urls and other useful features for tokenisation
'REGEX_tokenizer' : '''[dnlcsDNLCS]['’][^\W_]+''',

# Stop words and swadesh list (latter used extensively for language detection and keyword extraction when Xapian DB is not present)
'stops' : ("a","abord","absolument","afin","ah","ai","aie","aient","aies","ailleurs","ainsi","ait","allaient","allo","allons","allô","alors","anterieur","anterieure","anterieures","apres","après","as","assez","attendu","au","aucun","aucune","aucuns","aujourd","aujourd'hui","aupres","auquel","aura","aurai","auraient","aurais","aurait","auras","aurez","auriez","aurions","aurons","auront","aussi","autant","autre","autrefois","autrement","autres","autrui","aux","auxquelles","auxquels","avaient","avais","avait","avant","avec","avez","aviez","avions","avoir","avons","ayant","ayez","ayons","b","bah","bas","basee","bat","beau","beaucoup","bien","bigre","bon","boum","bravo","brrr","c","car","ce","ceci","cela","celle","celle-ci","celle-là","celles","celles-ci","celles-là","celui","celui-ci","celui-là","celà","cent","cependant","certain","certaine","certaines","certains","certes","ces","cet","cette","ceux","ceux-ci","ceux-là","chacun","chacune","chaque","cher","chers","chez","chiche","chut","chère","chères","ci","cinq","cinquantaine","cinquante","cinquantième","cinquième","clac","clic","combien","comme","comment","comparable","comparables","compris","concernant","contre","couic","crac","d","da","dans","de","debout","dedans","dehors","deja","delà","depuis","dernier","derniere","derriere","derrière","des","desormais","desquelles","desquels","dessous","dessus","deux","deuxième","deuxièmement","devant","devers","devra","devrait","different","differentes","differents","différent","différente","différentes","différents","dire","directe","directement","dit","dite","dits","divers","diverse","diverses","dix","dix-huit","dix-neuf","dix-sept","dixième","doit","doivent","donc","dont","dos","douze","douzième","dring","droite","du","duquel","durant","dès","début","désormais","e","effet","egale","egalement","egales","eh","elle","elle-même","elles","elles-mêmes","en","encore","enfin","entre","envers","environ","es","essai","est","et","etant","etc","etre","eu","eue","eues","euh","eurent","eus","eusse","eussent","eusses","eussiez","eussions","eut","eux","eux-mêmes","exactement","excepté","extenso","exterieur","eûmes","eût","eûtes","f","fais","faisaient","faisant","fait","faites","façon","feront","fi","flac","floc","fois","font","force","furent","fus","fusse","fussent","fusses","fussiez","fussions","fut","fûmes","fût","fûtes","g","gens","h","ha","haut","hein","hem","hep","hi","ho","holà","hop","hormis","hors","hou","houp","hue","hui","huit","huitième","hum","hurrah","hé","hélas","i","ici","il","ils","importe","j","je","jusqu","jusque","juste","k","l","la","laisser","laquelle","las","le","lequel","les","lesquelles","lesquels","leur","leurs","longtemps","lors","lorsque","lui","lui-meme","lui-même","là","lès","m","ma","maint","maintenant","mais","malgre","malgré","maximale","me","meme","memes","merci","mes","mien","mienne","miennes","miens","mille","mince","mine","minimale","moi","moi-meme","moi-même","moindres","moins","mon","mot","moyennant","multiple","multiples","même","mêmes","n","na","naturel","naturelle","naturelles","ne","neanmoins","necessaire","necessairement","neuf","neuvième","ni","nombreuses","nombreux","nommés","non","nos","notamment","notre","nous","nous-mêmes","nouveau","nouveaux","nul","néanmoins","nôtre","nôtres","o","oh","ohé","ollé","olé","on","ont","onze","onzième","ore","ou","ouf","ouias","oust","ouste","outre","ouvert","ouverte","ouverts","o|","où","p","paf","pan","par","parce","parfois","parle","parlent","parler","parmi","parole","parseme","partant","particulier","particulière","particulièrement","pas","passé","pendant","pense","permet","personne","personnes","peu","peut","peuvent","peux","pff","pfft","pfut","pif","pire","pièce","plein","plouf","plupart","plus","plusieurs","plutôt","possessif","possessifs","possible","possibles","pouah","pour","pourquoi","pourrais","pourrait","pouvait","prealable","precisement","premier","première","premièrement","pres","probable","probante","procedant","proche","près","psitt","pu","puis","puisque","pur","pure","q","qu","quand","quant","quant-à-soi","quanta","quarante","quatorze","quatre","quatre-vingt","quatrième","quatrièmement","que","quel","quelconque","quelle","quelles","quelqu'un","quelque","quelques","quels","qui","quiconque","quinze","quoi","quoique","r","rare","rarement","rares","relative","relativement","remarquable","rend","rendre","restant","reste","restent","restrictif","retour","revoici","revoilà","rien","s","sa","sacrebleu","sait","sans","sapristi","sauf","se","sein","seize","selon","semblable","semblaient","semble","semblent","sent","sept","septième","sera","serai","seraient","serais","serait","seras","serez","seriez","serions","serons","seront","ses","seul","seule","seulement","si","sien","sienne","siennes","siens","sinon","six","sixième","soi","soi-même","soient","sois","soit","soixante","sommes","son","sont","sous","souvent","soyez","soyons","specifique","specifiques","speculatif","stop","strictement","subtiles","suffisant","suffisante","suffit","suis","suit","suivant","suivante","suivantes","suivants","suivre","sujet","superpose","sur","surtout","t","ta","tac","tandis","tant","tardive","te","tel","telle","tellement","telles","tels","tenant","tend","tenir","tente","tes","tic","tien","tienne","tiennes","tiens","toc","toi","toi-même","ton","touchant","toujours","tous","tout","toute","toutefois","toutes","treize","trente","tres","trois","troisième","troisièmement","trop","très","tsoin","tsouin","tu","té","u","un","une","unes","uniformement","unique","uniques","uns","v","va","vais","valeur","vas","vers","via","vif","vifs","vingt","vivat","vive","vives","vlan","voici","voie","voient","voilà","voire","vont","vos","votre","vous","vous-mêmes","vu","vé","vôtre","vôtres","w","x","y","z","zut","à","â","ça","ès","étaient","étais","était","étant","état","étiez","étions","été","étée","étées","étés","êtes","être","ô"),
'swadesh' : (
'je',
'tu', 
'vous',
'il',
'nous',
'vous',
'ils',
'ceci',
'cela',
'ici',
'là',
'qui',
'quoi',
'où',
'quand',
'comment',
'ne pas',
'tout',
'beaucoup',
'quelques',
'peu',
'autre',
'un',
'deux',
'trois',
'quatre',
'cinq',
'grand',
'long',
'large',
'épais',
'lourd',
'petit',
'court',
'étroit',
'mince',
'femme',
'homme',
'homme',
'enfant',
'femme', 
'épouse',
'mari', 
'époux',
'mère',
'père',
'animal',
'poisson',
'oiseau',
'chien',
'pou',
'serpent',
'ver',
'arbre',
'forêt',
'bâton',
'fruit',
'graine',
'feuille',
'racine',
'écorce',
'fleur',
'herbe',
'corde',
'peau',
'viande',
'sang',
'os',
'graisse',
'œuf',
'corne',
'queue',
'plume',
'cheveux',
'tête',
'oreille',
'œil',
'nez',
'bouche',
'dent',
'langue',
'ongle',
'pied',
'jambe',
'genou',
'main',
'aile',
'ventre',
'entrailles', 
'intestins',
'cou',
'dos',
'poitrine',
'cœur',
'foie',
'boire',
'manger',
'mordre',
'sucer',
'cracher',
'vomir',
'souffler',
'respirer',
'rire',
'voir',
'entendre',
'savoir',
'penser',
'sentir',
'craindre',
'dormir',
'vivre',
'mourir',
'tuer',
'se battre',
'chasser',
'frapper',
'couper',
'fendre',
'poignarder',
'gratter',
'creuser',
'nager',
'voler',
'marcher',
'venir',
"s'étendre",
"être",
"étendu",
"s'asseoir",
"être", 
"assis",
'se', 
'lever',
'tenir',
'tourner',
'tomber',
'donner',
'tenir',
'serrer',
'frotter',
'laver',
'essuyer',
'tirer',
'pousser',
'jeter', 
'lancer',
'lier',
'coudre',
'compter',
'dire',
'chanter',
'jouer',
'flotter',
'couler',
'geler',
'gonfler',
'soleil',
'lune',
'étoile',
'eau',
'pluie',
'rivière',
'lac',
'mer',
'sel',
'pierre',
'sable',
'poussière',
'terre',
'nuage',
'brouillard',
'ciel',
'vent',
'neige',
'glace',
'fumée',
'feu',
'cendre',
'brûler',
'route',
'montagne',
'rouge',
'vert',
'jaune',
'blanc',
'noir',
'nuit',
'jour',
'an', 
'année',
'chaud',
'froid',
'plein',
'nouveau',
'vieux',
'bon',
'mauvais',
'pourri',
'sale',
'droit',
'rond',
'tranchant',
'émoussé',
'lisse',
'mouillé',
'sec',
'juste',
'près',
'loin',
'droite',
'gauche',
'à',
'dans',
'avec',
'et',
'si',
'parce' 
'que',
'nom',
),

'copulas' : (),

# Normalize strange chars in tokens
'token_replacements' : {
'‘' : "'",
'’' : "'",
},


# Aliases will be expanded upon tokenization, case sensitive
'aliases' :          {},


# Morphology type and -fixes
'morphology' : 1,
'prefixes' : (),
'suffixes' : (),
'name_suffixes' : (),
'infixes' : (),




# List of common words for lookups (faster than dictionaries in most cases), easily found on the internet
'commons' : (
    """de""",
    """la""",
    """le""",
    """et""",
    """les""",
    """des""",
    """en""",
    """un""",
    """du""",
    """une""",
    """que""",
    """est""",
    """pour""",
    """qui""",
    """dans""",
    """a""",
    """par""",
    """plus""",
    """pas""",
    """au""",
    """sur""",
    """ne""",
    """se""",
    """Le""",
    """ce""",
    """il""",
    """sont""",
    """La""",
    """Les""",
    """ou""",
    """avec""",
    """son""",
    """Il""",
    """aux""",
    """d’un""",
    """En""",
    """cette""",
    """d’une""",
    """ont""",
    """ses""",
    """mais""",
    """comme""",
    """on""",
    """tout""",
    """nous""",
    """sa""",
    """Mais""",
    """fait""",
    """été""",
    """aussi""",
    """leur""",
    """bien""",
    """peut""",
    """ces""",
    """y""",
    """deux""",
    """A""",
    """ans""",
    """l""",
    """encore""",
    """n’est""",
    """marché""",
    """d""",
    """Pour""",
    """donc""",
    """cours""",
    """qu’il""",
    """moins""",
    """sans""",
    """C’est""",
    """Et""",
    """si""",
    """entre""",
    """Un""",
    """Ce""",
    """faire""",
    """elle""",
    """c’est""",
    """peu""",
    """vous""",
    """Une""",
    """prix""",
    """On""",
    """dont""",
    """lui""",
    """également""",
    """Dans""",
    """effet""",
    """pays""",
    """cas""",
    """De""",
    """millions""",
    """Belgique""",
    """BEF""",
    """mois""",
    """leurs""",
    """taux""",
    """années""",
    """temps""",
    """groupe""",
    """ainsi""",
    """toujours""",
    """société""",
    """depuis""",
    """tous""",
    """soit""",
    """faut""",
    """Bruxelles""",
    """fois""",
    """quelques""",
    """sera""",
    """entreprises""",
    """F""",
    """contre""",
    """francs""",
    """je""",
    """n'a""",
    """Nous""",
    """Cette""",
    """dernier""",
    """était""",
    """Si""",
    """s’est""",
    """chez""",
    """L""",
    """monde""",
    """alors""",
    """sous""",
    """actions""",
    """autres""",
    """Au""",
    """ils""",
    """reste""",
    """trois""",
    """non""",
    """notre""",
    """doit""",
    """nouveau""",
    """milliards""",
    """avant""",
    """exemple""",
    """compte""",
    """belge""",
    """premier""",
    """s""",
    """nouvelle""",
    """Elle""",
    """l’on""",
    """terme""",
    """avait""",
    """produits""",
    """cela""",
    """d’autres""",
    """fin""",
    """niveau""",
    """bénéfice""",
    """toute""",
    """travail""",
    """partie""",
    """trop""",
    """hausse""",
    """secteur""",
    """part""",
    """beaucoup""",
    """Je""",
    """valeur""",
    """croissance""",
    """rapport""",
    """USD""",
    """aujourd’hui""",
    """année""",
    """base""",
    """Bourse""",
    """lors""",
    """vers""",
    """souvent""",
    """vie""",
    """l’entreprise""",
    """autre""",
    """peuvent""",
    """bon""",
    """surtout""",
    """toutes""",
    """nombre""",
    """fonds""",
    """point""",
    """grande""",
    """jour""",
    """va""",
    """avoir""",
    """nos""",
    """quelque""",
    """place""",
    """grand""",
    """personnes""",
    """plusieurs""",
    """certains""",
    """d'affaires""",
    """permet""",
    """politique""",
    """cet""",
    """chaque""",
    """chiffre""",
    """pourrait""",
    """devrait""",
    """produit""",
    """l'année""",
    """Par""",
    """rien""",
    """mieux""",
    """celui""",
    """qualité""",
    """France""",
    """Ils""",
    """Ces""",
    """s'agit""",
    """vente""",
    """jamais""",
    """production""",
    """action""",
    """baisse""",
    """Avec""",
    """résultats""",
    """Des""",
    """votre""",
    """risque""",
    """début""",
    """banque""",
    """an""",
    """voir""",
    """avons""",
    """qu’un""",
    """qu’""",
    """elles""",
    """moment""",
    """qu’on""",
    """question""",
    """pouvoir""",
    """titre""",
    """doute""",
    """long""",
    """petit""",
    """d’ailleurs""",
    """notamment""",
    """FB""",
    """droit""",
    """qu’elle""",
    """heures""",
    """cependant""",
    """service""",
    """Etats-Unis""",
    """qu’ils""",
    """l’action""",
    """jours""",
    """celle""",
    """demande""",
    """belges""",
    """ceux""",
    """services""",
    """bonne""",
    """seront""",
    """économique""",
    """raison""",
    """car""",
    """situation""",
    """Depuis""",
    """entreprise""",
    """me""",
    """nouvelles""",
    """n’y""",
    """possible""",
    """toutefois""",
    """tant""",
    """nouveaux""",
    """selon""",
    """parce""",
    """dit""",
    """seul""",
    """qu’une""",
    """sociétés""",
    """vient""",
    """jusqu’""",
    """quatre""",
    """marchés""",
    """mise""",
    """seulement""",
    """Van""",
    """semble""",
    """clients""",
    """Tout""",
    """Cela""",
    """serait""",
    """fort""",
    """frais""",
    """lieu""",
    """gestion""",
    """font""",
    """quand""",
    """capital""",
    """gouvernement""",
    """projet""",
    """grands""",
    """réseau""",
    """l’autre""",
    """données""",
    """prendre""",
    """plan""",
    """points""",
    """outre""",
    """pourtant""",
    """Ainsi""",
    """ni""",
    """type""",
    """Europe""",
    """pendant""",
    """Comme""",
    """mesure""",
    """actuellement""",
    """public""",
    """dire""",
    """important""",
    """mis""",
    """partir""",
    """parfois""",
    """nom""",
    """n’ont""",
    """veut""",
    """présent""",
    """passé""",
    """forme""",
    """autant""",
    """développement""",
    """mettre""",
    """grandes""",
    """vue""",
    """investisseurs""",
    """D""",
    """trouve""",
    """maison""",
    """mal""",
    """l’an""",
    """moyen""",
    """choix""",
    """doivent""",
    """NLG""",
    """direction""",
    """Sur""",
    """simple""",
    """période""",
    """enfants""",
    """dollars""",
    """personnel""",
    """assez""",
    """programme""",
    """général""",
    """banques""",
    """eux""",
    """semaine""",
    """président""",
    """personne""",
    """européenne""",
    """moyenne""",
    """tard""",
    """loi""",
    """petite""",
    """certaines""",
    """savoir""",
    """loin""",
    """explique""",
    """plupart""",
    """jeunes""",
    """cinq""",
    """contrat""",
    """Banque""",
    """valeurs""",
    """seule""",
    """rendement""",
    """nombreux""",
    """fonction""",
    """offre""",
    """client""",
    """activités""",
    """eu""",
    """environ""",
    """ministre""",
    """cadre""",
    """sens""",
    """étaient""",
    """sécurité""",
    """recherche""",
    """Paris""",
    """sorte""",
    """décembre""",
    """Son""",
    """suite""",
    """davantage""",
    """ensuite""",
    """janvier""",
    """donne""",
    """vrai""",
    """cause""",
    """d'abord""",
    """conditions""",
    """suis""",
    """juin""",
    """peine""",
    """certain""",
    """septembre""",
    """sommes""",
    """famille""",
    """l’indice""",
    """pris""",
    """laquelle""",
    """directeur""",
    """qu’en""",
    """propose""",
    """gens""",
    """derniers""",
    """étant""",
    """fut""",
    """chose""",
    """portefeuille""",
    """obligations""",
    """afin""",
    """différents""",
    """technique""",
    """Aujourd’hui""",
    """ailleurs""",
    """P""",
    """l’ensemble""",
    """américain""",
    """ventes""",
    """Selon""",
    """rue""",
    """livre""",
    """octobre""",
    """vraiment""",
    """sein""",
    """Or""",
    """dollar""",
    """Enfin""",
    """haut""",
    """Plus""",
    """petits""",
    """porte""",
    """tel""",
    """durée""",
    """domaine""",
    """aurait""",
    """jeune""",
    """présente""",
    """passe""",
    """PC""",
    """lorsque""",
    """choses""",
    """puis""",
    """Vous""",
    """aucun""",
    """l'un""",
    """n'en""",
    """tandis""",
    """coup""",
    """existe""",
    """propre""",
    """carte""",
    """crise""",
    """importante""",
    """atteint""",
    """revenus""",
    """montant""",
    """forte""",
    """ici""",
    """s’il""",
    """Quant""",
    """vu""",
    """rapidement""",
    """j’ai""",
    """ville""",
    """etc""",
    """mars""",
    """s’en""",
    """mon""",
    """premiers""",
    """bas""",
    """marque""",
    """véritable""",
    """ligne""",
    """longtemps""",
    """propres""",
    """devant""",
    """passer""",
    """départ""",
    """pu""",
    """total""",
    """série""",
    """quoi""",
    """particulier""",
    """concurrence""",
    """élevé""",
    """position""",
    """connu""",
    """principe""",
    """tendance""",
    """court""",
    """n""",
    """pages""",
    """évidemment""",
    """résultat""",
    """aura""",
    """parmi""",
    """Sans""",
    """américaine""",
    """face""",
    """trouver""",
    """durant""",
    """femmes""",
    """construction""",
    """désormais""",
    """distribution""",
    """telle""",
    """difficile""",
    """autour""",
    """européen""",
    """pratique""",
    """centre""",
    """vendre""",
    """juillet""",
    """mai""",
    """région""",
    """sociale""",
    """filiale""",
    """film""",
    """h""",
    """besoin""",
    """mode""",
    """Pas""",
    """représente""",
    """réalité""",
    """femme""",
    """vaut""",
    """Tél""",
    """aucune""",
    """hommes""",
    """donner""",
    """titres""",
    """l’Europe""",
    """nombreuses""",
    """différentes""",
    """moyens""",
    """formation""",
    """chiffres""",
    """Générale""",
    """dix""",
    """prochain""",
    """l’Etat""",
    """genre""",
    """bureau""",
    """communication""",
    """participation""",
    """gros""",
    """pourquoi""",
    """estime""",
    """devient""",
    """réalisé""",
    """création""",
    """novembre""",
    """l’évolution""",
    """pourra""",
    """semaines""",
    """consommation""",
    """faible""",
    """terrain""",
    """site""",
    """droits""",
    """moitié""",
    """puisque""",
    """Du""",
    """reprise""",
    """compris""",
    """projets""",
    """avril""",
    """vont""",
    """call""",
    """donné""",
    """simplement""",
    """six""",
    """firme""",
    """perte""",
    """Bien""",
    """Philippe""",
    """sait""",
    """prend""",
    """vite""",
    """via""",
    """stratégie""",
    """vos""",
    """jeu""",
    """J’""",
    """petites""",
    """marketing""",
    """presque""",
    """Michel""",
    """manque""",
    """réaliser""",
    """financiers""",
    """Car""",
    """Comment""",
    """voiture""",
    """chef""",
    """constitue""",
    """Internet""",
    """J’ai""",
    """enfin""",
    """net""",
    """charge""",
    """nature""",
    """second""",
    """payer""",
    """actuel""",
    """Elles""",
    """investissements""",
    """dispose""",
    """financier""",
    """d'achat""",
    """membres""",
    """date""",
    """avaient""",
    """gamme""",
    """revanche""",
    """comment""",
    """décision""",
    """l'avenir""",
    """tour""",
    """actionnaires""",
    """s'y""",
    """solution""",
    """créer""",
    """l'économie""",
    """concerne""",
    """l'époque""",
    """belle""",
    """lequel""",
    """tél""",
    """seconde""",
    """version""",
    """Pays-Bas""",
    """cher""",
    """chacun""",
    """lire""",
    """techniques""",
    """décidé""",
    """mouvement""",
    """conseil""",
    """nécessaire""",
    """meilleur""",
    """double""",
    """sujet""",
    """généralement""",
    """restent""",
    """celles""",
    """politiques""",
    """malgré""",
    """confiance""",
    """homme""",
    """d'actions""",
    """Certains""",
    """ayant""",
    """papier""",
    """commerce""",
    """Région""",
    """Wallonie""",
    """Windows""",
    """termes""",
    """met""",
    """contraire""",
    """informations""",
    """l’industrie""",
    """trimestre""",
    """E""",
    """différence""",
    """certaine""",
    """formule""",
    """jusqu'au""",
    """voit""",
    """programmes""",
    """actuelle""",
    """permis""",
    """dossier""",
    """Quand""",
    """l'heure""",
    """guerre""",
    """acheter""",
    """rendre""",
    """février""",
    """ma""",
    """l'emploi""",
    """main""",
    """voire""",
    """bons""",
    """technologie""",
    """européens""",
    """Sa""",
    """éléments""",
    """unique""",
    """l'eau""",
    """venir""",
    """générale""",
    """courant""",
    """suffit""",
    """l'ordre""",
    """conserver""",
    """maximum""",
    """force""",
    """fax""",
    """Que""",
    """largement""",
    """milliard""",
    """soient""",
    """Pierre""",
    """devenir""",
    """l'Union""",
    """franc""",
    """minimum""",
    """mort""",
    """responsable""",
    """possibilité""",
    """presse""",
    """affaires""",
    """longue""",
    """travers""",
    """M""",
    """BBL""",
    """relativement""",
    """moi""",
    """Deux""",
    """présence""",
    """européennes""",
    """devraient""",
    """groupes""",
    """ensemble""",
    """santé""",
    """New""",
    """pense""",
    """bénéfices""",
    """but""",
    """compagnie""",
    """publique""",
    """coeur""",
    """revenu""",
    """mesures""",
    """table""",
    """nettement""",
    """questions""",
    """d'avoir""",
    """permettre""",
    """l'homme""",
    """Chez""",
    """retour""",
    """qu'elles""",
    """C""",
    """majorité""",
    """potentiel""",
    """moindre""",
    """récemment""",
    """secteurs""",
    """réduction""",
    """large""",
    """traitement""",
    """perdu""",
    """étrangers""",
    """parents""",
    """l'une""",
    """fond""",
    """capacité""",
    """vitesse""",
    """activité""",
    """l'exercice""",
    """l'objet""",
    """quel""",
    """tient""",
    """taille""",
    """éviter""",
    """risques""",
    """Jean""",
    """Pourtant""",
    """Allemagne""",
    """parler""",
    """propos""",
    """quant""",
    """signifie""",
    """voie""",
    """jouer""",
    """prévoit""",
    """blanc""",
    """noir""",
    """parti""",
    """logiciel""",
    """continue""",
    """Notre""",
    """bois""",
    """meilleure""",
    """l'argent""",
    """perspectives""",
    """développer""",
    """celui-ci""",
    """oeuvre""",
    """structure""",
    """suivre""",
    """tiers""",
    """prise""",
    """professionnels""",
    """raisons""",
    """néanmoins""",
    """preuve""",
    """social""",
    """bénéficiaire""",
    """couleurs""",
    """mondial""",
    """Cet""",
    """maintenant""",
    """essentiellement""",
    """prévu""",
    """Japon""",
    """prévisions""",
    """centrale""",
    """Alors""",
    """international""",
    """yeux""",
    """PME""",
    """l'a""",
    """ait""",
    """bonnes""",
    """opérations""",
    """pied""",
    """l'art""",
    """pourraient""",
    """Londres""",
    """juge""",
    """devra""",
    """uniquement""",
    """corps""",
    """divers""",
    """Parmi""",
    """numéro""",
    """réduire""",
    """Tous""",
    """texte""",
    """tenu""",
    """budget""",
    """l'étranger""",
    """pression""",
    """mes""",
    """n'était""",
    """style""",
    """économiques""",
    """Jacques""",
    """montre""",
    """population""",
    """analystes""",
    """S""",
    """processus""",
    """placement""",
    """classique""",
    """dividende""",
    """rester""",
    """publics""",
    """fortement""",
    """plein""",
    """wallonne""",
    """DEM""",
    """Express""",
    """faudra""",
    """travailler""",
    """Crédit""",
    """directement""",
    """prime""",
    """Flandre""",
    """crédit""",
    """monnaie""",
    """précise""",
    """appel""",
    """Autre""",
    """travaux""",
    """l'occasion""",
    """juste""",
    """Chaque""",
    """put""",
    """tableau""",
    """terre""",
    """permettent""",
    """devenu""",
    """rouge""",
    """mémoire""",
    """partenaires""",
    """rapide""",
    """travailleurs""",
    """joue""",
    """objectif""",
    """salle""",
    """parle""",
    """musique""",
    """milieu""",
    """d'entreprise""",
    """autorités""",
    """chute""",
    """régime""",
    """d'autant""",
    """liste""",
    """opération""",
    """bout""",
    """performances""",
    """électronique""",
    """haute""",
    """responsables""",
    """lancé""",
    """voitures""",
    """patron""",
    """Malgré""",
    """affiche""",
    """situe""",
    """B""",
    """l'image""",
    """études""",
    """Microsoft""",
    """condition""",
    """retrouve""",
    """Aux""",
    """revient""",
    """Belgacom""",
    """route""",
    """Ensuite""",
    """Luxembourg""",
    """campagne""",
    """comptes""",
    """hors""",
    """culture""",
    """Commission""",
    """d'entre""",
    """possibilités""",
    """semestre""",
    """actifs""",
    """finalement""",
    """internationale""",
    """l'achat""",
    """monétaire""",
    """passage""",
    """of""",
    """justice""",
    """page""",
    """tels""",
    """poids""",
    """celle-ci""",
    """commercial""",
    """entendu""",
    """l'investisseur""",
    """mondiale""",
    """accord""",
    """diverses""",
    """totalement""",
    """fil""",
    """clair""",
    """vin""",
    """biens""",
    """euro""",
    """York""",
    """parfaitement""",
    """viennent""",
    """division""",
    """réseaux""",
    """principal""",
    """lancer""",
    """supérieur""",
    """atteindre""",
    """référence""",
    """téléphone""",
    """management""",
    """vins""",
    """proche""",
    """collection""",
    """fiscale""",
    """Ceci""",
    """informatique""",
    """investissement""",
    """volume""",
    """matériel""",
    """publicité""",
    """train""",
    """coupon""",
    """progression""",
    """tenir""",
    """protection""",
    """l'aide""",
    """couleur""",
    """nouvel""",
    """Lorsque""",
    """change""",
    """changement""",
    """garantie""",
    """somme""",
    """Belge""",
)

}


# Stem commons
if model.get('stemmer') != None:
    stemmer = snowballstemmer.stemmer(model.get('stemmer','english'))
    commons_stemmed = []
    for w in model.get('commons',''):
        w = stemmer.stemWord(w)
        commons_stemmed.append(w)
    model['commons_stemmed'] = tuple(commons_stemmed)

# Generate pickle file
filename = model['names'][0] + '_model.pkl'

with open(filename, "wb") as write_file:
    pickle.dump(model, write_file)


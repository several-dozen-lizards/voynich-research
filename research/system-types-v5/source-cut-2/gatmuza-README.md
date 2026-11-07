# Lo GAT MUZA: CATMUS-conformant HTR Ground-Truth Data for Medieval Occitan

[![DOI](https://zenodo.org/badge/1187281108.svg)](https://doi.org/10.5281/zenodo.21135195)

## Introduction

This repository provides a dataset to train handwritten text recognition models for Medieval Occitan manuscripts.

It is based on a selection of pages from a handful of medieval manuscripts, selected to provide generic, typologic and textual diversity.

All transcriptions have been systematically compared to reference editions by the transcriber (J.B. Camps). 

|language | century | script | ms | N. Pages | N. Cols | Detailed loc.|
|-----|-----|-----|-----|-----|-----|-----|
|pro | 13 | textualis | BnF, fr. 1592, chansonnier B | 2 | 4 | Italie (Provence for Brunel; Auvergne for Zufferey), end 13th-beg. 14th c. (mid 13th for Zufferey)|
|pro | 13th-14th | textualis | BnF, fr. 2164, Jaufre, A | 2 | 4 | Nîmes, 1281-1320|
|pro | 14 | textualis | Montpellier AA9, Petit Thalamus de Montpellier | 2 | 2 | 1320|
|pro | 13 | textualis | BnF, fr. 2180, Girart de Rossilhon, P | 4 | 4 | Périgord, 13th, 2nd half|
|pro | 13 | textualis | Carcassonne, BM 34 (Flamenca) | 10 | 10 | Provence? End 13th|
|pro | 14 | cursiva, semihybrida | BnF, NAF 4232 (Passion Didot, Daurel et Beton) | 12 | 12 | Region of Albi, 14th c.|
|pro | 14 | cursiva | BnF, fr. 12472, chansonnier f | 4 | 4 | Provence, 14th for Brunel; 14th, first half and region of Arles for the DOM|


## Dataset Overview

The data adheres to the Segmonto guidelines for layout, and to the CATMUS Guidelines for transcription. Accordingly,

- abbreviations are not expanded;
- word segmentation is modernised, except for elision (e.g., _lamor_, _mamor_, etc.);
- the characters used are those described in: https://catmus-guidelines.github.io/

## Citation

If you use this dataset in your research, please cite it as follows:

> Camps, Jean-Baptiste. Lo GAT MUZA: CATMUS-conformant HTR Ground-Truth Data for Medieval Occitan [Data set]. https://github.com/LostMa-ERC/gatmuza.

## Reference Editions

- BnF, fr. 1592, chansonnier B: Concordance de l'Occitan Médiéval, ed. P. Ricketts.
- BnF, fr. 2164, Jaufre, A: Clovis Brunel, Jaufré: Roman Arthurien du XIIIe Siècle en Vers Provençaux, 1943, https://archive.org/details/JaufreTomeI/page/n177/mode/2up.
- Montpellier AA9, Petit Thalamus de Montpellier: Équipe projet Thalamus, Édition critique numérique du manuscrit AA9 des Archives municipales de Montpellier dit Le Petit Thalamus. Université Paul Valéry Montpellier-III, 2014-.... En ligne : http://thalamus.huma-num.fr/.
- BnF, fr. 2180, Girart de Rossilhon, P: 	Girartz de Rossilho, nach der Pariser Handschrift herausgegeben von Dr. Conr. Hofmann, 1857, https://archive.org/details/diewerkedertroubepischehof.
- Carcassonne, BM 34 (Flamenca): Paul Meyer, Le roman de Flamenca; publié d'après le manuscrit unique de Carcassonne, 1901, https://archive.org/details/leromandeflamenc01meyeuoft.
- BnF, NAF 4232 (Passion Didot): La Passion provençale du manuscrit Didot, mystère du XIVe siècle publié par William P. Shephard, 1928, https://archive.org/details/lapassionprovencaleshephe/.
- BnF, NAF 4232 (Passion Didot, Daurel et Beton): Paul Meyer, Daurel et Beton : chanson de geste provençale, 1880, https://archive.org/details/daureletbetonch00meye/.
- BnF, fr. 12472, chansonnier f: Corpus dell’antico occitano: Edizione interpretativa del canzoniere f; Parigi, Bibliothèque nationale de France, fr. 12472, a cura di Fabio Barberini, 2019, https://www.rialto.unina.it/wp-content/uploads/2023/02/f.pdf.


## Funding and Support

Funded by the European Union (ERC, LostMA, 101117408). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the
 European Research Council. Neither the European Union nor the granting authority can be held responsible for them.

This work has received support under the Major Research Program of PSL Research University ``CultureLab'' launched by PSL Research University and implemented by ANR with the references ANR-10-IDEX-0001.

## License

This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).  
You are free to share and adapt the material, provided appropriate credit is given.



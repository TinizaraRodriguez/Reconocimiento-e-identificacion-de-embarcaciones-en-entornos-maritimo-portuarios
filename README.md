# Reconocimiento e identificación de embarcaciones en entornos maritimos-portuarios

This repository contains the code, resources and tools necessary for the development and execution of the project: ‘Reconocimiento e identificación de embarcaciones en entornos maritimos-portuarios’ presented at the University of Las Palmas de Gran Canaria (ULPGC).
The main objective of the project is to implement and evaluate different algorithms that allow the accurate identification of ship registration using OCR technology.


# Index
<ul style="list-style-type: none;">
  <li style="list-style-type: none;"><strong></strong><a href="#2">Getting Started</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#3">Files structure</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#4">Installing</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#5">Built with</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#6">Authors</a></li
  <li style="list-style-type: none;"><strong></strong><a href="#7">Supervisors</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#8">License</a></li>
  <li style="list-style-type: none;"><strong></strong><a href="#9">Contact</a></li>
</ul>


## Getting Started <div id="2" />


### Files structure <div id="3" />

- **Dockerfiles/**: Contains the Dockerfiles needed to build the two containers used to test the algorithms.
- **Dataset/**: Includes the dataset categorised by image type, used to run and analyse each algorithm.
- **Scripts/**: Folder with the scripts needed to implement and run the different models.
- **Checkpoints/**: Stores the checkpoints for MixNet and Clip4str necessary for the correct execution.
- **Models_Directory/**: Directory for the model utilities needed for the execution of the scripts.


### Installing <div id="4" />


### Built With <div id="5" />

* [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
* [EasyOCR](https://github.com/JaidedAI/EasyOCR)
* [KerasOCR](https://github.com/faustomorales/keras-ocr) 
* [PyTesseract](https://github.com/h/pytesseract) 
* [MixNet](https://github.com/D641593/MixNet) 
* [Clip4STR](https://github.com/VamosC/CLIP4STR) 


## Authors <div id="6" />

* **Tinizara María Rodríguez Delgado**


## Supervisors <div id="7" />
* **Nelson Monzón López**
* **Jonay Suárez Ramírez**
* **Leopoldo López Reverón**

## License <div id="8" />
This software is proprietary and confidential. Unauthorized copying of this file, via any medium, is strictly prohibited. All rights reserved.

## Contact <div id="9" />
For further information, contact via email:

Tinizara María Rodríguez Delgado: tinizara.rodriguez101@alu.ulpgc.es

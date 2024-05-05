<h1>Lego-Brick-Sorter</h1>
Project utilizing TensorFlow and OpenCV to classify and sort Lego bricks into different categories

<br></br>

<h2>Piece Image Capture:</h2>
Will utilize our webcam with OpenCV to capture pieces on a moving conveyor belt. Experimentation found that the MOG2 background subtractor worked best here.

![ezgif-3-d4c07acc58](https://github.com/Billiam2468/Lego-Brick-Sorter/assets/2740224/558b6816-c81e-4b50-bba4-04eedfee22bb)

Apologies for the poor video quality. Will get proper screen recordings later.

<h2>Synthetic Data Generation:</h2>
Since I don't have a dataset of all Lego pieces that have ever been in production to train on, I relied on synthetic data generation using 3D models of Lego bricks using the LDraw library. Using Blenders Python API, I was able to use these 3D models, simulate the dropping of pieces in random positions, with randomized backgrounds to prevent overfitting and create 10,000 images for the database of ~1500 pieces, coming out to roughly 15 million synthetic images.

Setup of Blender Python Script

Sample of Images Created

<h2>Model Training:</h2>

<h2>Model Training Benchmarks (GRAPHS OF TRAINING AND VALIDATION ACCURACY HERE):</h2>
Training on our real data set (images captured from our conveyor belt):

1. Model v1:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) --> Real world accuracy ~37%
2. Model v1.1:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with random noise/color background --> Real world accuracy ~50% (But low validation acc for some reason?)
3. Model v1.2:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with data augmentation --> Real world accuracy ~75%
4. Model v2.0:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with all techniques above + fine-tuning on real world data --> RW Categorical Accuracy ~93.3
5. **Model v3.0:**
* ResNet50 transfer-trained fully on synthetic data --> RWCA AVG 81% --> Fine-Tuned --> **RWCA AVG 95.69%**
<br></br>

<h2>Resources Used:</h2>
<div style="white-space: nowrap;">
  <img src="https://img.shields.io/badge/github-%23181717.svg?&style=for-the-badge&logo=github&logoColor=white" style="display: inline-block; margin-right: 10px;">
  <img src="https://img.shields.io/badge/blender-%23F5792A.svg?&style=for-the-badge&logo=blender&logoColor=white" style="display: inline-block; margin-right: 10px;">
  <img src="https://img.shields.io/badge/python-%233776AB.svg?&style=for-the-badge&logo=python&logoColor=white" style="display: inline-block; margin-right: 10px;">
  <img src="https://img.shields.io/badge/jupyter-%23F37626.svg?&style=for-the-badge&logo=jupyter&logoColor=white" style="display: inline-block; margin-right: 10px;">
  <img src="https://img.shields.io/badge/opencv-%235C3EE8.svg?&style=for-the-badge&logo=opencv&logoColor=white" style="display: inline-block; margin-right: 10px;">
  <img src="https://img.shields.io/badge/tensorflow-%23FF6F00.svg?&style=for-the-badge&logo=tensorflow&logoColor=white" style="display: inline-block; margin-right: 10px">
  <img src="https://www.ldraw.org/common/images/banners/default/main.png" style="display: inline-block; margin-right: 10px; height: 30px">
</div>

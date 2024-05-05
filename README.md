<h1>Lego-Brick-Sorter</h1>
Project utilizing TensorFlow and OpenCV to classify and sort Lego bricks into different categories

<br>

<h2>Piece Image Capture:</h2>
I utilized a Logitech C310 webcam and OpenCV to film pieces on a moving conveyor belt. Experimentation found that the MOG2 background subtractor worked best here to isolate pieces from the moving background.

![ezgif-3-d4c07acc58](https://github.com/Billiam2468/Lego-Brick-Sorter/assets/2740224/558b6816-c81e-4b50-bba4-04eedfee22bb)

Apologies for the poor video quality. Will get proper screen recordings later.

<h2>Synthetic Data Generation:</h2>
Since I don't have a dataset of all Lego pieces that have ever been in production to train on, I relied on synthetic data generation using 3D models of Lego bricks using the LDraw library. Using Blenders Python API, I was able to use these 3D models, simulate the dropping of pieces in random positions, with randomized backgrounds to prevent overfitting and create 10,000 images for the database of ~1500 pieces, coming out to roughly 15 million synthetic images.

<h3>Blender Piece Drop Sequence:</h3>

![drop video (online-video-cutter com)](https://github.com/Billiam2468/Lego-Brick-Sorter/assets/2740224/9bf3e8b4-4c95-4dfe-8e30-9c482eabb343)


<h3>Sample of Images Created:</h3>

![Screenshot from 2024-05-05 16-46-12](https://github.com/Billiam2468/Lego-Brick-Sorter/assets/2740224/e03da7d1-6ee2-493a-a5af-c90416fdb506)

<h2>Model Training:</h2>
Finally I initiated model training using our fully synthetic database. Prior to training on our raw synthetic images, I implemented several preprocessing functions including horizontal reflections, color channel shifts, and Gaussian blur. These steps were aimed at introducing diversity into our images and, crucially, preventing overfitting to artificially generated Lego pieces. Instead of starting from scratch, I employed transfer learning with the ResNet50 model, utilizing its pre-trained capabilities in image categorization to classify Lego bricks. Initially trained exclusively on synthetic data, I then refined the model's performance by fine-tuning it with real-world images, bridging the gap between artificial and real-world datasets.

<h2>Model Performance (100 classes):</h2>
Performance: 59/59 - 31s - loss: 0.3236 - <b>categorical_accuracy: 0.8985</b> - 31s/epoch - 522ms/step

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

# Lego-Brick-Sorter
Will be using TensorFlow and OpenCV, to sort lego bricks into different categories

<br></br>

**Benchmarks:**
This involves training a model and testing on our real data set

1. Model v1:
* Trained fully on synthetic data (4 classes) --> Real world accuracy ~37%
2. Model v1.1:
* Trained fully on synthetic data (4 classes) with random noise/color background --> Real world accuracy ~50% (But low validation acc for some reason?)
3. Model v1.2:
*  Trained fully on synthetic data (4 classes) with data augmentation --> Real world accuracy ~75%

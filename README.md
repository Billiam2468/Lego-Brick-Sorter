# Lego-Brick-Sorter
Will be using TensorFlow and OpenCV, to sort lego bricks into different categories

<br></br>

**Beginning Benchmarks:**
This involves training a model on four classes and testing on our real data set

1. Model v1:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) --> Real world accuracy ~37%
2. Model v1.1:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with random noise/color background --> Real world accuracy ~50% (But low validation acc for some reason?)
3. Model v1.2:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with data augmentation --> Real world accuracy ~75%
4. Model v2.0:
* DenseNet169 transfer-trained fully on synthetic data (4 classes) with all techniques above + fine-tuning on real world data --> RW Categorical Accuracy ~93.3
5. **Model v3.0:**
* ResNet50 transfer-trained fully on synthetic data --> RWCA AVG 81% --> Fine-Tuned --> RWCA AVG **95.69%**
* We will use this one!

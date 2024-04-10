from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt
from IPython import display
from sklearn.cluster import KMeans
import numpy as np

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)

fig, ax1 = plt.subplots()
ax1.set_title('Training Digit Frequency')
ax1.set_ylabel('Number of Images')
ax1.set_label('Digit 0-9')
ax1.hist(y_train, np.arange(0, 11, 1), ec='black')
ax1.set_xticks(np.arange(0, 10, 1))

fig, ax2 = plt.subplots()
ax2.set_title('Testing Digit Frequency')
ax2.set_ylabel('Number of Images')
ax2.set_label('Digit 0-9')
ax2.hist(y_test, np.arange(0, 11, 1), ec='black')
ax2.set_xticks(np.arange(0, 10, 1))

nestedList = [[] for x in range(10)]
for x in range(len(x_train)):
  nestedList[y_train[x]].append(x_train[x])
x_train = nestedList

nestedList = [[] for x in range(10)]
for x in range(len(x_test)):
  nestedList[y_test[x]].append(x_test[x])
x_test = nestedList

for x in range(10):
    fig, ax3 = plt.subplots(3, 3, figsize=(8, 8))
    temp = np.array(nestedList[x])
    clusters = KMeans(n_clusters = 10).fit(temp.reshape(temp.shape[0], 784))
    labels = clusters.labels_
    centroids = clusters.cluster_centers_

    for y in range(len(centroids)):
        I = centroids[y].reshape(28, 28)
        if y < 9:
          ax3[int(y / 3), y % 3].imshow(I, cmap='gray')
          ax3[int(y / 3), y % 3].set_title(f'Label: {str(int(x))} Cluster {str(y)}', fontsize=16)
          ax3[int(y / 3), y % 3].axis('off')
    plt.show()

    prediction = clusters.predict()
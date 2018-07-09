'''
  demo_mnv2_deeplab_v3+_tf

  these codes base on https://colab.research.google.com/github/tensorflow/models/blob/master/research/deeplab/deeplab_demo.ipynb

Author: Zhengwei Li
Data: July 3 2018 
'''
import tensorflow as tf
import argparse
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
from PIL import Image

import numpy as np
import time
from matplotlib import gridspec
from matplotlib import pyplot as plt

import pdb
# paramers 
parser = argparse.ArgumentParser()

parser.add_argument('--model_pb', default='./pre_train/deeplabv3_mnv2_pascal_trainval/frozen_inference_graph.pb')
parser.add_argument('--image', default='./image/')
args = parser.parse_args()


from graphviz import Digraph

def tf_to_dot(graph):
    dot = Digraph()

    for n in graph.as_graph_def().node:
        dot.node(n.name, label=n.name)

        for i in n.input:
            dot.edge(i, n.name)
            
    return dot



def create_pascal_label_colormap():
  """Creates a label colormap used in PASCAL VOC segmentation benchmark.

  Returns:
    A Colormap for visualizing segmentation results.
  """
  colormap = np.zeros((256, 3), dtype=int)
  ind = np.arange(256, dtype=int)

  for shift in reversed(range(8)):
    for channel in range(3):
      colormap[:, channel] |= ((ind >> channel) & 1) << shift
    ind >>= 3

  return colormap


def label_to_color_image(label):
  """Adds color defined by the dataset colormap to the label.

  Args:
    label: A 2D array with integer type, storing the segmentation label.

  Returns:
    result: A 2D array with floating type. The element of the array
      is the color indexed by the corresponding element in the input label
      to the PASCAL color map.

  Raises:
    ValueError: If label is not of rank 2 or its value is larger than color
      map maximum entry.
  """
  if label.ndim != 2:
    raise ValueError('Expect 2-D input label')

  colormap = create_pascal_label_colormap()

  if np.max(label) >= len(colormap):
    raise ValueError('label value too large.')

  return colormap[label]


def vis_segmentation(image, seg_map):
  """Visualizes input image, segmentation map and overlay view."""
  plt.figure(figsize=(15, 5))
  grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])

  plt.subplot(grid_spec[0])
  plt.imshow(image)
  plt.axis('off')
  plt.title('input image')

  plt.subplot(grid_spec[1])
  seg_image = label_to_color_image(seg_map).astype(np.uint8)
  plt.imshow(seg_image)
  plt.axis('off')
  plt.title('segmentation map')

  plt.subplot(grid_spec[2])
  plt.imshow(image)
  plt.imshow(seg_image, alpha=0.7)
  plt.axis('off')
  plt.title('segmentation overlay')

  unique_labels = np.unique(seg_map)
  ax = plt.subplot(grid_spec[3])
  plt.imshow(
      FULL_COLOR_MAP[unique_labels].astype(np.uint8), interpolation='nearest')
  ax.yaxis.tick_right()
  plt.yticks(range(len(unique_labels)), LABEL_NAMES[unique_labels])
  plt.xticks([], [])
  ax.tick_params(width=0.0)
  plt.grid('off')
  plt.show()

LABEL_NAMES = np.asarray([
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tv'
])

FULL_LABEL_MAP = np.arange(len(LABEL_NAMES)).reshape(len(LABEL_NAMES), 1)
FULL_COLOR_MAP = label_to_color_image(FULL_LABEL_MAP)


#@title Helper methods


class DeepLabModel(object):
  """Class to load deeplab model and run inference."""

  INPUT_TENSOR_NAME = 'ImageTensor:0'
  OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
  INPUT_SIZE = 513
  FROZEN_GRAPH_NAME = 'frozen_inference_graph'

  def __init__(self, args):
    """Creates and loads pretrained deeplab model."""
    self.graph = tf.Graph()
    graph_def = tf.GraphDef()
    with open(args.model_pb, "rb") as f:
      graph_def.ParseFromString(f.read())

    if graph_def is None:
      raise RuntimeError('Cannot find inference graph in tar archive.')
    with self.graph.as_default():
      tf.import_graph_def(graph_def, name='')

    self.sess = tf.Session(graph=self.graph)

    # ------------     
    # dot = tf_to_dot(self.graph)
    # dot.render('mnv2_dpv3', view=True)

 
  def run(self, image):
    """Runs inference on a single image.

    Args:
      image: A PIL.Image object, raw input image.

    Returns:
      resized_image: RGB image resized from original input image.
      seg_map: Segmentation map of `resized_image`.
    """
    width, height = image.size
    resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
    target_size = (int(resize_ratio * width), int(resize_ratio * height))
    resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
    batch_seg_map = self.sess.run(
      self.OUTPUT_TENSOR_NAME,
      feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
 
    # for v in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES): 
    #   if v.name.endswith('weights:0'):
    #     print(v)
    seg_map = batch_seg_map[0]

    return resized_image, seg_map


  def get_weights(self):
    '''
      get weights in the graph
    '''

    from collections import OrderedDict
    state_dict = OrderedDict()
    # print weights 
    with self.graph.as_default():

      for op in tf.get_default_graph().get_operations():
        # print(op.name)
        if (op.name.rfind('weights') != -1 and op.name.rfind('read') == -1) \
            or (op.name.rfind('biases') != -1 and op.name.rfind('read') == -1):
          print (op.name)
          state_dict[op.name] = []

    pdb.set_trace()

    # get paramers
    for key in state_dict.keys():
      state_dict[key] = self.sess.run(key + ':0')

    return state_dict

  def save_graph(self):
    '''
      save graph to dir, then use: tensorboard --logdir=dir
      Attention ! Use after run() !
    '''
    with self.sess:
      writer = tf.summary.FileWriter("output", self.sess.graph)
      writer.close()
# -----------------------------------------------------------------------------
# main
# 
def main(args):

  mnv2_dpv3 = DeepLabModel(args)
  paramers =  mnv2_dpv3.get_weights()
  
  # input 
  image = Image.open(args.image)

  # run
  t0 = time.time()
  resized_image, seg_map = mnv2_dpv3.run(image)
  print(time.time() - t0)

  # visal
  vis_segmentation(resized_image, seg_map)

  # save graph
  # mnv2_dpv3.save_graph()



if __name__ == "__main__":
  main(args)





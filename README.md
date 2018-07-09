# Demo_mobilenetv2_deeplabv3
Semantic segmentation demo bases on [tensorflow official demo](https://github.com/tensorflow/models/blob/master/research/deeplab)


# Usage
To use the demo, you should download pretrain_model(**mobilenetv2_coco_voc_trainaug** or **mobilenetv2_coco_voc_trainval**) from[here](https://github.com/tensorflow/models/blob/master/research/deeplab/g3doc/model_zoo.md) 
firstly. 

Then, unzip model file to dir(like ./pre_train). 

Finally run:

    python3 demo_mnv2_deeplab_v3.py \
    --model_pb ./pre_train/deeplabv3_mnv2_pascal_trainval/frozen_inference_graph.pb \
    --input [your image path]

# Requirements
- python3
- tensorflow >= 1.4 (cpu or gpu)



# demo_mobilenetv2_deeplabv3
semantic segmentation demo bases on https://github.com/lizhengwei1992/models/tree/master/research/deeplab

# Usage
To use the demo, you should download pretrain_model(mobilenetv2_coco_voc_trainaug or mobilenetv2_coco_voc_trainval) from here[https://github.com/tensorflow/models/blob/master/research/deeplab/g3doc/model_zoo.md] firstly. Then, unzip model file to dir(like pre_train). Finally run:

    python/python3 demo_mnv2_deeplab_v3.py \
    --model_pb ./pre_train/deeplabv3_mnv2_pascal_trainval/frozen_inference_graph.pb \
    --input [your image path]




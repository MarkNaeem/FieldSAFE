#! /usr/bin/env python3

import rospy

from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError

from detectron2.data import MetadataCatalog
from detectron2.utils.logger import setup_logger

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer




class image_converter:

  def __init__(self):

    rospy.init_node('mask_rcnn')

    setup_logger()

    self.cfg = get_cfg()
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
    self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"))
    self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
    self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml")
    self.predictor = DefaultPredictor(self.cfg)

    self.image_pub = rospy.Publisher("/Logitech_webcam/image_masked",Image,queue_size=10)

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/Logitech_webcam/image_raw/compressed",CompressedImage,self.callback)
    
    rospy.loginfo("masked_rcnn loaded into the converter!")

  def callback(self,data):
    try:
      cv_image = self.bridge.compressed_imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      rospy.logerr(e)

    outputs = self.predictor(cv_image)
    v = Visualizer(cv_image[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), scale=1.0)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu")).get_image()

    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(out, "bgr8"))
    except CvBridgeError as e:
      rospy.logerr(e)

def main():

    ic = image_converter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
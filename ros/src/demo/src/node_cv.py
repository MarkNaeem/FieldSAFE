#! /usr/bin/env python3
import cv2
import rospy
from imutils.object_detection import non_max_suppression

from numpy import array
from sensor_msgs.msg import  CompressedImage, Image
from cv_bridge import CvBridge, CvBridgeError




class image_converter:

  def __init__(self):


    rospy.init_node('yolact_ros_node')


    self.hog = cv2.HOGDescriptor()
    self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())



    self.image_pub = rospy.Publisher("/Logitech_webcam/image_masked",Image,queue_size=10)

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/Logitech_webcam/image_raw/compressed",CompressedImage,self.callback)
    
    rospy.loginfo("yolact model loaded!")

  def callback(self,data):
    try:
      cv_image = self.bridge.compressed_imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      rospy.logerr(e)

    (rects, weights) = self.hog.detectMultiScale(cv_image, winStride=(4, 4),padding=(8, 8), scale=1.05)
    rects = array([[x, y, x + w, y + h] for (x, y, w, h) in rects])    
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(cv_image, (xA, yA), (xB, yB), (0, 255, 0), 2)

    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
    except CvBridgeError as e:
      rospy.logerr(e)

def main():

    ic = image_converter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        rospy.logerr("Shutting down")

if __name__ == '__main__':
    main()


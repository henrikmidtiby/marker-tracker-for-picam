# Import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import MarkerTracker
import math


def annotate_frame_with_detected_marker(frame, marker_pose, order_of_marker_input, size_of_kernel_input,
                                        track_orientation):
    line_width_of_circle = 2
    if marker_pose.quality > 0.5:
        marker_color = (0, 255, 0)
    else:
        marker_color = (255, 0, 255)
    cv2.circle(frame, (marker_pose.x, marker_pose.y), int(size_of_kernel_input / 2), marker_color, line_width_of_circle)
    dist = 50
    direction_line_width = 1
    if track_orientation:
        # Mark the orientation of the detected marker
        point1 = (marker_pose.x, marker_pose.y)
        point2 = (math.trunc(marker_pose.x + dist * math.cos(marker_pose.theta)),
                  math.trunc(marker_pose.y + dist * math.sin(marker_pose.theta)))

        cv2.line(frame, point1, point2, marker_color, direction_line_width)
    else:
        point1 = (marker_pose.x, marker_pose.y)
        theta = marker_pose.theta
        for k in range(order_of_marker_input):
            theta += 2 * math.pi / order_of_marker_input
            point2 = (math.trunc(marker_pose.x + dist * math.cos(theta)),
                      math.trunc(marker_pose.y + dist * math.sin(theta)))

            cv2.line(frame, point1, point2, marker_color, direction_line_width)

def main():
    # Initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    resolution = (640, 480)
    resolution = (320, 240)
    resolution = (160, 120)
    #resolution = (80, 60)
    camera.resolution = resolution
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=resolution)

    # Allot the camera to warmup
    time.sleep(0.1)

    tracker = MarkerTracker.MarkerTracker(4, 15, 1)
    tracker.track_marker_with_missing_black_leg = False

    # Capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # gra the raw NumPy array representing the image, then initialize
        # the timestamp and occupied/unoccupied text.
        image = frame.array

        greyscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        pose = tracker.locate_marker(greyscale_image)
        timestring = time.strftime("%H:%M:%S", time.gmtime())
        print("%s %4d %4d %6.2f %6.3f" % (timestring, pose.x, pose.y, pose.theta, pose.quality))

	annotate_frame_with_detected_marker(image, pose, 4, 20, False)
        # show the fram
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the nect frame
        rawCapture.truncate(0)

        # if the 'q' key was pressed, break from the loop
        if key == ord('q'):
            break

main()


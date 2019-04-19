import cv2
import numpy as np
import imutils
import time

def DrawPoint( x, y, radius, blue, green, red, output):
    cv2.circle(output, (int(x), int(y)), int(radius), (blue, green, red), -1)

def CreateBlankCanvas(width, height, blue, green, red):
    return np.full((height, width, 3), (blue, green, red), np.uint8)

def DrawLine(ox, oy, nx, ny, thickness, blue, green, red, output):
    output = cv2.line(output, (int(ox), int(oy)), (int(nx), int(ny)),(blue, green, red), thickness)


if __name__ == "__main__":

    orangeLower = (8, 150, 115)
    orangeUpper = (20, 255, 241)

    oldX = int(0)
    oldY = int(0)

    canvas = CreateBlankCanvas(600, 460, 255, 255, 255)

    videoInput = cv2.VideoCapture(0)
    time.sleep(1.0)

    while True:
        ret, frame = videoInput.read()

        frame = np.fliplr(frame)
        frame = imutils.resize(frame, width=600)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, orangeLower, orangeUpper)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                if (ox == 0 and oy == 0):
                    DrawPoint(x, y, 6, 255, 0, 0, canvas)
                else:
                    DrawLine(oldX, oldY, x, y, 6, 255, 0, 0, canvas)
            oldX = x
            oldY = y

        cv2.imshow("Frame", frame)
        cv2.imshow("Canvas", canvas)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    videoInput.release()
    cv2.destroyAllWindows()
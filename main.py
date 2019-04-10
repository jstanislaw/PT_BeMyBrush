import cv2
import numpy as np
import time


if __name__ == "__main__":

    videoInput = cv2.VideoCapture(0)
    time.sleep(1.0)

    while True:
        ret, frame = videoInput.read()

        frame = np.fliplr(frame)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    videoInput.release()
    cv2.destroyAllWindows()
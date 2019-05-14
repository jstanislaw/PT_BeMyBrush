import cv2
import numpy as np
import imutils
import time

def DrawPoint( x, y, radius, blue, green, red, output):
    cv2.circle(output, (int(x), int(y)), int(radius), (blue, green, red), -1)

def CreateBlankCanvas(width, height, blue, green, red):
    return np.full((height, width, 3), (blue, green, red), np.uint8)

def DrawLine(ox, oy, nx, ny, thickness, blue, green, red, output):
    cv2.line(output, (int(ox), int(oy)), (int(nx), int(ny)),(blue, green, red), thickness)

def nothing(x):
    pass

if __name__ == "__main__":

    alpha = 0.8
    beta = (1-alpha)

    orangeLower = (8, 150, 115)
    orangeUpper = (20, 255, 241)

    ox = int(0)
    oy = int(0)

    canvas = CreateBlankCanvas(600, 460, 0, 111, 230)

    videoInput = cv2.VideoCapture(0)
    time.sleep(1.0)

    tn = True

    cv2.namedWindow('Frame')
    cv2.createTrackbar('R', 'Frame', 0, 255, nothing)
    cv2.createTrackbar('G', 'Frame', 0, 255, nothing)
    cv2.createTrackbar('B', 'Frame', 0, 255, nothing)
    cv2.createTrackbar('Rubber', 'Frame', 0, 1, nothing)
    cv2.createTrackbar('Brush Size', 'Frame', 10, 40, nothing)

    brush_color = [0, 0, 0]
    canvas_color = [0, 111, 230]

    while True:
        ret, frame = videoInput.read()

        frame = np.fliplr(frame)
        frame = imutils.resize(frame, width=600)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, orangeLower, orangeUpper)

        brush_color[0] = cv2.getTrackbarPos('B', 'Frame')
        brush_color[1] = cv2.getTrackbarPos('G', 'Frame')
        brush_color[2] = cv2.getTrackbarPos('R', 'Frame')
        rubber = cv2.getTrackbarPos('Rubber', 'Frame')
        brush_size = cv2.getTrackbarPos('Brush Size', 'Frame')

        if( tn ):
            canvas = CreateBlankCanvas(frame.shape[1], frame.shape[0], canvas_color[0], canvas_color[1], canvas_color[2])
            tn = False

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)


        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts) > 0:
            #print("(" + str(ox) + "," + str(oy)+")")
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(brush_size), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                if(ox == 0 and oy == 0):
                    if(rubber == 0):
                        DrawPoint(x, y, brush_size, brush_color[0], brush_color[1], brush_color[2], canvas)
                    else:
                        DrawPoint(x, y, brush_size, canvas_color[0], canvas_color[1], canvas_color[2], canvas)

                else:
                   if(abs(ox-x)<25 and abs(oy-y)<25):
                       if(rubber == 0):
                           DrawLine(ox, oy, x, y, brush_size, brush_color[0], brush_color[1], brush_color[2], canvas)
                       else:
                           DrawLine(ox, oy, x, y, brush_size, canvas_color[0], canvas_color[1], canvas_color[2], canvas)

            ox = x
            oy = y


        output = cv2.addWeighted(frame, alpha, canvas, beta, 0.0)
        merged1 = np.hstack((output, canvas))
        merged2 = np.vstack((CreateBlankCanvas(1200, 20, brush_color[0], brush_color[1], brush_color[2]), merged1 ))

        cv2.imshow("Frame", merged2)


        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    videoInput.release()
    cv2.destroyAllWindows()
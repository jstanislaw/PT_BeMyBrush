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

def WriteToFile(Ol, Ou):
    ParametersFile = open("Resources/Config.txt", "w")

    ParametersFile.write(str(Ol[0]) + '\n')
    ParametersFile.write(str(Ol[1]) + '\n')
    ParametersFile.write(str(Ol[2]) + '\n')
    ParametersFile.write(str(Ou[0]) + '\n')
    ParametersFile.write(str(Ou[1]) + '\n')
    ParametersFile.write(str(Ou[2]) + '\n')

    ParametersFile.close()

def ReadFromFile(nr):
    ParametersFile = open('Resources/Config.txt')
    try:
        tekst = ParametersFile.read()
    finally:
        ParametersFile.close()

    x = tekst.split('\n')
    i=0

    for a in range(6):
        nr[i] = int(x[i])
        i=i+1


if __name__ == "__main__":

    nr = [0, 0, 0, 0, 0, 0]

    ReadFromFile(nr)

    alpha = 0.8
    beta = (1-alpha)

    orangeLower = (nr[0], nr[1], nr[2])
    orangeUpper = (nr[3], nr[4], nr[5])

    videoInput2 = cv2.VideoCapture(0)
    time.sleep(1.0)

    cv2.namedWindow('Frame', 0)
    cv2.createTrackbar('OL H', 'Frame', orangeLower[0], 179, nothing)
    cv2.createTrackbar('OL S', 'Frame', orangeLower[1], 255, nothing)
    cv2.createTrackbar('OL V', 'Frame', orangeLower[2], 255, nothing)
    cv2.createTrackbar('OU H', 'Frame', orangeUpper[0], 179, nothing)
    cv2.createTrackbar('OU S', 'Frame', orangeUpper[1], 255, nothing)
    cv2.createTrackbar('OU V', 'Frame', orangeUpper[2], 255, nothing)

    while True:
        ret2, frame2 = videoInput2.read()

        frame2 = np.fliplr(frame2)
        frame2 = imutils.resize(frame2, width=600)
        hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
        mask2 = cv2.inRange(hsv2, orangeLower, orangeUpper)

        orangeLower = (cv2.getTrackbarPos('OL H', 'Frame'), cv2.getTrackbarPos('OL S', 'Frame'), cv2.getTrackbarPos('OL V', 'Frame'))
        orangeUpper = (cv2.getTrackbarPos('OU H', 'Frame'), cv2.getTrackbarPos('OU S', 'Frame'), cv2.getTrackbarPos('OU V', 'Frame'))


        cv2.imshow("Frame", mask2)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('\r'): # carriage return
            break

    videoInput2.release()
    cv2.destroyWindow('Frame')

    WriteToFile(orangeLower, orangeUpper)

    print(orangeLower)
    print(orangeUpper)


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
    cv2.createTrackbar('Brush Size', 'Frame', 1, 40, nothing)

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

        if(tn):
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
        merged2 = np.vstack((merged1, CreateBlankCanvas(1200, 20, brush_color[0], brush_color[1], brush_color[2])))

        cv2.imshow("Frame", merged2)


        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    videoInput.release()
    cv2.destroyAllWindows()
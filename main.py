import cv2
import numpy as np
import imutils
import time
import os


def DrawPoint(x, y, radius, blue, green, red, output):
    cv2.circle(output, (int(x), int(y)), int(radius), (blue, green, red), -1)


def CreateBlankCanvas(width, height, blue, green, red):
    return np.full((height, width, 3), (blue, green, red), np.uint8)


def DrawLine(ox, oy, nx, ny, thickness, blue, green, red, output):
    cv2.line(output, (int(ox), int(oy)), (int(nx), int(ny)), (blue, green, red), thickness)


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
    i = 0

    for a in range(6):
        nr[i] = int(x[i])
        i += 1


#zapis obrazu do pliku
def SaveFile(cs, image):

    if cs == 1:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        if not os.path.exists("SavedImages"):
            os.mkdir("SavedImages")
        cv2.imwrite("SavedImages/Picture%s.jpg" % timestr, image)


def calibration():

    nr = [0, 0, 0, 179, 255, 255]
    ReadFromFile(nr)

    orangeLower = (nr[0], nr[1], nr[2])
    orangeUpper = (nr[3], nr[4], nr[5])

    label  = cv2.imread('Resources/Label.png', cv2.IMREAD_GRAYSCALE)

    videoInput2 = cv2.VideoCapture(0)
    time.sleep(1.0)

    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.createTrackbar('Hue Min', "Trackbars", orangeLower[0], 179, nothing)
    cv2.createTrackbar('Saturaton Min', "Trackbars", orangeLower[1], 255, nothing)
    cv2.createTrackbar('Value Min', "Trackbars", orangeLower[2], 255, nothing)
    cv2.createTrackbar('Hue Max', "Trackbars", orangeUpper[0], 179, nothing)
    cv2.createTrackbar('Saturation Max', "Trackbars", orangeUpper[1], 255, nothing)
    cv2.createTrackbar('Value Max', "Trackbars", orangeUpper[2], 255, nothing)

    while True:
        cal_ret, cal_frame = videoInput2.read()
        cal_frame = np.fliplr(cal_frame)
        cal_frame = imutils.resize(cal_frame, width=600)
        cal_hsv = cv2.cvtColor(cal_frame, cv2.COLOR_BGR2HSV)

        Hmin = cv2.getTrackbarPos('Hue Min', "Trackbars")
        SMin = cv2.getTrackbarPos('Saturaton Min', "Trackbars")
        VMin = cv2.getTrackbarPos('Value Min', "Trackbars")
        HMax = cv2.getTrackbarPos('Hue Max', "Trackbars")
        SMax = cv2.getTrackbarPos('Saturation Max', "Trackbars")
        VMax = cv2.getTrackbarPos('Value Max', "Trackbars")

        orangeLower = (Hmin, SMin, VMin)
        orangeUpper = (HMax, SMax, VMax)

        cal_mask = cv2.inRange(cal_hsv, orangeLower, orangeUpper)

        cal_mask = cv2.erode(cal_mask, None, iterations=2)
        cal_mask = cv2.dilate(cal_mask, None, iterations=3)

        # cv2.moveWindow("Trackbars", 250, 150)
        # cv2.moveWindow("Mask", 555, 145)

        cv2.imshow("Trackbars", label)
        cv2.imshow("Mask", cal_mask)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('\r'):  # carriage return
            enabled = True
            break

        if cv2.getWindowProperty("Mask", 0) < 0:
            enabled = False
            break

        if cv2.getWindowProperty("Trackbars", 0) < 0:
            enabled = False
            break

    videoInput2.release()
    cv2.destroyAllWindows()

    WriteToFile(orangeLower, orangeUpper)

    print(orangeLower)
    print(orangeUpper)

    return orangeLower, orangeUpper, enabled


def drawing():
    cansave = 1

    ox = int(0)
    oy = int(0)

    alpha = 0.9
    beta = (1.0 - alpha)

    canvas_color = [255, 255, 255]
    canvas = CreateBlankCanvas(600, 450, canvas_color[0], canvas_color[1], canvas_color[2])
    interface = cv2.imread('Resources/Interface.png', cv2.IMREAD_COLOR)

    videoInput = cv2.VideoCapture(0)
    time.sleep(1.0)

    # tn = True

    cv2.namedWindow('BeMyBrush', cv2.WINDOW_AUTOSIZE)

    brush_color = [0, 0, 0]
    brush_size = 10
    rubber = False

    while True:
        ret, frame = videoInput.read()

        frame = np.fliplr(frame)
        frame = imutils.resize(frame, width=600)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, orangeLowerdrawing, orangeUpperdrawing)

        #        if tn :
        #            canvas = CreateBlankCanvas(frame.shape[1], frame.shape[0], canvas_color[0], canvas_color[1], canvas_color[2])
        #            tn = False

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if rubber:
            cv2.rectangle(frame, (int(105), int(2)), (int(245), int(37)), (0, 0, 255), thickness=2, lineType=8)
        else:
            cv2.rectangle(frame, (int(355), int(2)), (int(495), int(37)), (0, 0, 255), thickness=2, lineType=8)

        if brush_size == 30:
            cv2.rectangle(frame, (int(2), int(79)), (int(38), int(132)), (0, 0, 255), thickness=2, lineType=8)
        if brush_size == 25:
            cv2.rectangle(frame, (int(2), int(140)), (int(38), int(191)), (0, 0, 255), thickness=2, lineType=8)
        if brush_size == 20:
            cv2.rectangle(frame, (int(2), int(200)), (int(38), int(251)), (0, 0, 255), thickness=2, lineType=8)
        if brush_size == 10:
            cv2.rectangle(frame, (int(2), int(260)), (int(38), int(312)), (0, 0, 255), thickness=2, lineType=8)
        if brush_size == 5:
            cv2.rectangle(frame, (int(2), int(320)), (int(38), int(372)), (0, 0, 255), thickness=2, lineType=8)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            # M = cv2.moments(c)
            # center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (brush_color[0], brush_color[1], brush_color[2]), 2)
                cv2.circle(frame, (int(x), int(y)), brush_size - int(brush_size / 3),
                           (brush_color[0], brush_color[1], brush_color[2]), -1)

                if y > 40 and 40 < x < 560:
                    cansave = 1
                    if ox == 0 and oy == 0:
                        if rubber:
                            DrawPoint(x, y, brush_size, canvas_color[0], canvas_color[1], canvas_color[2], canvas)
                        else:
                            DrawPoint(x, y, brush_size, brush_color[0], brush_color[1], brush_color[2], canvas)

                    else:
                        if abs(ox - x) < 25 and abs(oy - y) < 25:
                            if rubber:
                                DrawLine(ox, oy, x, y, brush_size, canvas_color[0], canvas_color[1], canvas_color[2],
                                         canvas)
                            else:
                                DrawLine(ox, oy, x, y, brush_size, brush_color[0], brush_color[1], brush_color[2],
                                         canvas)

                else:
                    if y < 35:
                        if 100 < x < 250:
                            rubber = 1
                        if 350 < x < 500:
                            rubber = 0
                        if 0 < x < 100:
                            canvas = CreateBlankCanvas(frame.shape[1], frame.shape[0], canvas_color[0], canvas_color[1],
                                                       canvas_color[2])
                        if 250 < x < 350:
                            SaveFile(cansave, crap_canvas)
                            cv2.rectangle(frame, (int(255), int(2)), (int(345), int(37)), (0, 0, 255), thickness=2,
                                          lineType=8)
                            cansave = 0

                    if x < 35:
                        if 0 < y < 70:
                            canvas = CreateBlankCanvas(frame.shape[1], frame.shape[0], canvas_color[0], canvas_color[1],
                                                       canvas_color[2])
                        if 70 < y < 135:
                            brush_size = 30
                        if 135 < y < 195:
                            brush_size = 25
                        if 195 < y < 255:
                            brush_size = 20
                        if 255 < y < 315:
                            brush_size = 10
                        if 315 < y < 375:
                            brush_size = 5
                        if y > 375:
                            break  # wyjście
                    if x > 565:
                        if 0 < y < 45:
                            nothing(1)  # saveFile()
                        if 45 < y < 85:
                            brush_color = [255, 255, 255]  # biały
                        if 85 < y < 125:
                            brush_color = [0, 0, 0]  # czarny
                        if 125 < y < 165:
                            brush_color = [0, 0, 45]  # brązowy
                        if 165 < y < 205:
                            brush_color = [255, 0, 0]  # niebieski
                        if 205 < y < 245:
                            brush_color = [255, 255, 0]  # cyan
                        if 245 < y < 285:
                            brush_color = [0, 255, 0]  # zielony
                        if 285 < y < 325:
                            brush_color = [0, 0, 255]  # czerwony
                        if 325 < y < 365:
                            brush_color = [0, 128, 255]  # pomarańcz
                        if 365 < y < 405:
                            brush_color = [0, 255, 255]  # żółty
                        if 405 < y < 450:
                            brush_color = [255, 0, 255]  # magenta

            ox = x
            oy = y

        crap_canvas = canvas[40:450, 40:560]
        crap_canvas_res = imutils.resize(crap_canvas, height=450)
        output = cv2.addWeighted(frame, alpha, canvas, beta, 0.0)
        GUI = cv2.addWeighted(output, 0.5, interface, 0.5, 0.0)
        merged1 = np.hstack((GUI, crap_canvas_res))
        #merged2 = np.vstack((merged1, CreateBlankCanvas(1200, 20, brush_color[0], brush_color[1], brush_color[2])))

        cv2.imshow("BeMyBrush", merged1)

        key = cv2.waitKey(1) & 0xFF

        if cv2.getWindowProperty("BeMyBrush", 0) < 0:
            break

        if key == ord("q"):
            break

    videoInput.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

#--------------Kalibracja-----------------

    orangeLowerdrawing, orangeUpperdrawing, enabled = calibration()

#---------- Rysowanie ----------------
    if enabled:
        drawing()

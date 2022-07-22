#!/usr/bin/env python3
import cv2
import argparse
import numpy as np
from PIL import Image, ImageFilter
from skimage import color



# Cálculo de error
def deltaE(lab_est, lab_sample): 
    L_est = lab_est[0]
    a_est = lab_est[1]
    b_est = lab_est[2]

    L_samp = lab_sample[0]
    a_samp = lab_sample[1]
    b_samp = lab_sample[2]

    DL = L_samp - L_est
    Da = a_samp - a_est
    Db = b_samp - b_est

    DE = np.sqrt(DL**2 + Da**2 + Db**2)
    return DE, DL, Da, Db

def loadCCM(ccmCsvFile) :
    csvData = ccmCsvFile.read()
    lines = csvData.replace(' ', '').split('\n')
    del lines[len(lines) - 1]

    data = list()
    cells = list()

    for i in range(len(lines)):
        cells.append(lines[i].split(','))

    i = 0
    for line in cells:
        data.append(list())
        for j in range(len(line)):
            data[i].append(float(line[j]))
        i += 1
    return np.asarray(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ccm', action='store',
                        type=argparse.FileType('r'))
    parser.add_argument('input', action='store')
    parser.add_argument('output', action='store')
    parser.add_argument('-g', '--gamma', type=float, default=0.967, action='store',
                        help='Gamma value of source data. ')
    args = parser.parse_args()
    gamma = args.gamma

    ccm = loadCCM(args.ccm)
    input = cv2.imread(args.input) # BGR
    input = cv2.cvtColor(input,cv2.COLOR_BGR2RGB)/255 # RGB
    input_L = input**(1/gamma)  # rgb linealized 

    # Change to 2D to apply matrix; then change back.
    y, x, ch = input_L.shape 
    input_L = input_L.reshape(y*x,ch) # m*n x 3 

    # aplicar color correction matrix 
    correct = input_L@ccm 

    # Place limits on output.
    correct = np.minimum(correct,1) 
    correct = np.maximum(correct,0) 

    correct = correct**(1/2.2) # Apply gamma for sRGB, Adobe RGB color space.
    # Deal with saturated pixels. Not perfect, but this is what cameras do. Related to "purple fringing".
    correct[input_L==1.0] = 1.0 # Don't change saturated pixels. (We don't know HOW saturated.)
    correct = correct.reshape(y,x,ch) # mxnx3 RGB
    correct = cv2.cvtColor((correct*255).astype('uint8'),cv2.COLOR_RGB2BGR) # BGR
    cv2.imwrite(args.output, correct)


    # ESTAMPILLA ESTANDAR
    estandar = np.array([87.73,16.27,100.60]) # ESTANDAR 

    # MUESTRA 
    muestra = color.xyz2lab(xyz_img, illuminant= 'D50', observer='2')
    muestra = np.array([np.median(muestra[:,:,0]),np.median(muestra[:,:,1]),np.median(muestra[:,:,2])])

    # ERROR
    DE, DL, Da, Db = deltaE(estandar, muestra)

    print('DE = ' + str(DE))
    print('DL = ' + str(DL))
    print('Da = ' + str(Da))
    print('Db = ' + str(Db))

    # if DE <= 2.50: 
    #     print(': DeltaE = ' + str(round(DE,2)) + '  TRUE')
    # else: 
    #     print(': DeltaE = ' + str(round(DE,2)) + '  FALSE')

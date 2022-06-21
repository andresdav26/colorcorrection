#!/usr/bin/env python3
import cv2
import argparse
import numpy as np
from PIL import Image, ImageFilter
from skimage import color

# preprocessing 
def preprocess(I):
    If = I.filter(ImageFilter.MedianFilter(size = 25))  
    # I_lab = color.rgb2lab(If, illuminant= 'D65', observer='2')
    # I_lab[:,:,0] = 79.61
    # Ic = color.lab2rgb(I_lab, illuminant='D65',observer='2')
    # Ic = Image.fromarray(np.uint8(Ic*255))
    If.save(args.preprocess)
    return If

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

def gamma_table(gamma_r, gamma_g, gamma_b, gain_r=1.0, gain_g=1.0, gain_b=1.0):
    r_tbl = [min(255, int((x / 255.) ** (gamma_r) * gain_r * 255.)) for x in range(256)]
    g_tbl = [min(255, int((x / 255.) ** (gamma_g) * gain_g * 255.)) for x in range(256)]
    b_tbl = [min(255, int((x / 255.) ** (gamma_b) * gain_b * 255.)) for x in range(256)]
    return r_tbl + g_tbl + b_tbl

def applyGamma(img, gamma=2.2):
    inv_gamma = 1. / gamma
    return img.point(gamma_table(inv_gamma, inv_gamma, inv_gamma))

def deGamma(img, gamma=2.2):
    return img.point(gamma_table(gamma, gamma, gamma))

def sRGB2XYZ(img):
    # # D50
    rgb2xyz = (0.4360747, 0.3850649, 0.1430804, 0,
               0.2225045, 0.7168786, 0.0606169, 0,
               0.0139322, 0.0971045, 0.7141733, 0)
    # D65
    # rgb2xyz = (0.412391, 0.357584, 0.180481, 0,
    #            0.212639, 0.715169, 0.072192, 0,
    #            0.019331, 0.119195, 0.950532, 0)
    return img.convert("RGB", rgb2xyz)

def XYZ2sRGB(img):
    # D50
    xyz2rgb = (3.1338561, -1.6168667, -0.4906146, 0,
               -0.9787684,  1.9161415,  0.0334540, 0,
               0.0719453, -0.2289914,  1.4052427, 0)
    # D65
    # xyz2rgb = (3.240970, -1.537383, -0.498611, 0,
    #            -0.969244, 1.875968, 0.041555, 0,
    #            0.055630, -0.203977, 1.056972, 0)
    return img.convert("RGB", xyz2rgb)

def correctColor(img, ccm):
    return img.convert("RGB", tuple(ccm.transpose().flatten()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ccm', action='store',
                        type=argparse.FileType('r'))
    parser.add_argument('input', action='store')
    # parser.add_argument('preprocess', action='store')
    parser.add_argument('output', action='store')
    parser.add_argument('-g', '--gamma', type=float, default=2.2, action='store',
                        help='Gamma value of reference and source data. (Default=2.2)')
    args = parser.parse_args()
    gamma = args.gamma

    ccm = loadCCM(args.ccm)
    input_img = Image.open(args.input, 'r').convert('RGB').transpose(1).transpose(5)
    # input_img = preprocess(input_img)
    input_img = deGamma(input_img, gamma=gamma)
    input_img = sRGB2XYZ(input_img)
    input_img = correctColor(input_img, ccm)
    xyz_img = input_img # almacenar xyz corregido 
    input_img = XYZ2sRGB(input_img)
    input_img = applyGamma(input_img, gamma=gamma)
    input_img.save(args.output)


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

#!/bin/env python
from PIL import Image, ImageDraw
from sys import argv
from re import sub

mainRegex = "([^0-9.',]|\'.*\'|,$)"

def loadMatrix(filename):
    matrix = []
    f = open(filename, 'r')
    buf = f.readlines()
    f.close()
    for item in buf:
        data = sub(mainRegex, '', item).split(',')
        if len(data) > 2:
            tmp = list(map(lambda x: int(x), data))
            matrix.append(tmp)
    return matrix

if __name__ == '__main__':
    if len(argv) < 2:
        print('usage: {} <scale-factor> <matrix> <output-image>'.format(argv[0]))
        exit(0)
    matrix = loadMatrix(argv[2])
    imageSize = len(matrix)
    scaleFactor = int(argv[1])
    image = Image.new('RGBA', (imageSize*scaleFactor, imageSize*scaleFactor), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for i in range(imageSize):
        for j in range(imageSize):
            color = matrix[i][j] % 255
            draw.rectangle([(i*scaleFactor, j*scaleFactor), ((i-1)*scaleFactor, (j-1)*scaleFactor)], fill=(color, color, color))
    image.save(argv[3], 'PNG')
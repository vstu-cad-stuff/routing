#!/bin/env python
from PIL import Image, ImageDraw
from sys import argv
from re import sub

mainRegex = "([^0-9.',]|\'.*\'|,$)"

# load correspondence data
def loadMatrix(filename):
    # list for matrix
    matrix = []
    # read all lines from file
    f = open(filename, 'r')
    buf = f.readlines()
    f.close()
    for item in buf:
        # remove all unnecessary characters from a string (except digits and commas)
        # and divided into the list by commas
        data = sub(mainRegex, '', item).split(',')
        # if the string is not empty
        if len(data) > 2:
            # transform each element to int
            tmp = list(map(lambda x: int(x), data))
            # append list to matrix
            matrix.append(tmp)
    return matrix

if __name__ == '__main__':
    if len(argv) < 2:
        print('usage: {} <scale-factor> <matrix> <output-image>'.format(argv[0]))
        exit(0)
    # load matrix from file
    matrix = loadMatrix(argv[2])
    # get matrix size
    imageSize = len(matrix)
    # get image scale factor
    scaleFactor = int(argv[1])
    # create image
    image = Image.new('RGBA', (imageSize*scaleFactor, imageSize*scaleFactor), (0, 0, 0, 0))
    # get drawable context
    draw = ImageDraw.Draw(image)
    for i in range(imageSize):
        for j in range(imageSize):
            # get color from matrix
            color = matrix[i][j] % 255
            # draw rectangle in (i,j) position with color
            draw.rectangle([(i*scaleFactor, j*scaleFactor), ((i-1)*scaleFactor, (j-1)*scaleFactor)], fill=(color, color, color))
    # save image to file
    image.save(argv[3], 'PNG')
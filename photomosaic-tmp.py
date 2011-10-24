# @date:	2011-10-10
# @author:	ymeng7
from PIL import Image
import os, sys, time
import string
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer

# The "distance" function takes 2 pixels as input and returns the
# squared distance between them.
def distance(pix1, pix2):
        dist = 0
        for i in range(3):
                dist = dist + (pix1[i] - pix2[i])*(pix1[i] - pix2[i])
        return dist

# The "scale" function takes an image and the designated width and
# height factor and scale that image accordingly.
def scale(origImage, widthFactor, heightFactor):
        origsize = origImage.size
        w = (int) (origsize[0] * widthFactor) # width of the scaled image
        h = (int) (origsize[1] * heightFactor) # height of the scaled image
        newimg = Image.new("RGB",(w,h)) # a new blank image to store the scaled image
        for x in range(w):
                for y in range(h):
                        pxl=origImage.getpixel((((int)(x/widthFactor)),
                        ((int)(y/heightFactor)))) # take the pixel from the original image
                        newimg.putpixel((x,y),pxl) # store it into the new scaled image
        return newimg #pass on the new scaled image

# The "putBlock" function takes an image block and a base image
# and a location(a tuple specifying the location the pixel at the
# top-left corner of the image block should be put on the base
# image).
def putBlock(block, destImg, location):
        blocksize = block.size
        destsize = destImg.size
        try:
                for x in range(blocksize[0]):
                        for y in range(blocksize[1]):
                                pxl = block.getpixel((x,y))
                                destImg.putpixel((location[0]+x,
                                location[1]+y),pxl)
        except IndexError:
                print "Opsss... index error at: ", (x, y)

# The "average" function takes an image as input and it returns
# a pixel consists of the average color (over all the pixels 
# in the image) of each color channel.
def average(img):
        (r,g,b)=(0,0,0)
        size=img.size
        c=0
        try:
                for x in range(size[0]):
                        cnt = 0
                        (rr,gg,bb)=(0,0,0)
                        for y in range(size[1]):
                                tmp=img.getpixel((x,y))
                                rr += tmp[0]
                                gg += tmp[1]
                                bb += tmp[2]
                                cnt += 1
                        r+=(rr/cnt)
                        g+=(gg/cnt)
                        b+=(bb/cnt)
                        c+=1
                r/=c
                g/=c
                b/=c
        except TypeError:
                return None
        return (r,g,b)

# The "buildTile" function takes an image and a tileSize (a
# tuple specifying width and height) as input and it returns 
# a tile(a tuple consisting of a thumbnail image, together
# with the average color of the thumbnail).
def buildTile(img, tileSize):
        thumbnail = scaleTarget(img,tileSize)
        avg=average(img)
        if avg != None:
                return (thumbnail,avg)
        else:
                return None

#The function "scaleTarget" takes an image and a newSize (a 
# tuple specifying desired width and height) as input and it
# returns an image scaled to the given size.
def scaleTarget(img, newsize):
        origsize = img.size
        px = (newsize[0])/(float)(origsize[0])
        py = newsize[1]/ (float)(origsize[1])
        newimg = scale(img,px,py)
        return newimg

def findBestThumb(pixel, tileList):
        lowest = sys.maxint
#        print tileList[0][1]
        bestimg = None
        #print pixel
        for i in range(len(tileList)):
                dist = distance(pixel, tileList[i][1])
                if lowest >= dist:
                        #print tileList[i][1]
                        lowest = min(lowest,dist)
                        bestTile = tileList[i]
                        #print dist," while lowest: ", lowest
        #print "best fit is ",lowest
        return bestTile[0]

# The function "makeTileList" takes a list of image file names (strings)
# and a tile size as input and it returns a list of tiles, whose index
# corresponds to the index of the list of given image files.
def makeTileList(imageFileList, tileSize):
        tileList=[]
        widgets = ['Making #',Counter(), ' tile: ', Percentage(), ' ',
               Bar(marker='#',left='[',right=']'),
               ' ', ETA()]
        pbar = ProgressBar(widgets=widgets,maxval=len(imageFileList)).start()
        for item in range(len(imageFileList)):
                img = Image.open(imageFileList[item])
                tmp=buildTile(img, tileSize)
                if tmp != None:
                        tileList.append(tmp)
                try:
                        pbar.update(item)
                except ValueError:
                        pass
        pbar.finish()
        return tileList

def stitchMosaic(img, tileList):
        (width,height) = img.size
        (thubW,thubH) = (tileList[0][0]).size
        imgW = width * thubW
        imgH = height * thubH
        mosaic = Image.new("RGB",(imgW,imgH))
        (mosH,mosW)=(0,0)
        for w in range(width):
                mosH = 0
                for h in range(height):
                        mosW = 0
                        curPxl = img.getpixel((w,h))
                        pxlImg = findBestThumb(curPxl,tileList)
                        putBlock(pxlImg, mosaic, (w*thubW,h*thubH))
                        mosW += thubW
                mosH += thubH
        return mosaic
"""                        for ww in range(thubW):
                                for hh in range(thubH):
                                        try:
                                                pxl = pxlImg.getpixel((ww,hh))
                                        except IndexError:
                                                pxl = (0,0,0)
                                        mosaic.putpixel((w*thubW + ww,h*thubH +hh),pxl)"""

# the buildMosaic function orchestrates the creation of the mosaic.
# It requires a target image file, and directory of images to use
# as a tile library, a tile size, and a mosaic resolution, as input.
# Though it returns nothing, its effect is to save a photoMosaic in
# a .jpg file.
def buildMosaic(imageFile, imageDirectory, tileSize, resolution):
        # Create a list of image file names from a directory
        imgFileList = os.listdir(imageDirectory)
        for item in range(len(imgFileList)):
                imgFileList[item] = imageDirectory+os.sep+imgFileList[item]
        # Create a list of tiles by calling makeTileList.
        imgTileList = makeTileList(imgFileList,tileSize)
        # Scale target image by calling scaleTarget.
        target = scaleTarget(imageFile, resolution)
        # Create the mosaic image by calling stitchMosaic.
        mosaicImg=stitchMosaic(target,imgTileList)
        # Save the mosaic image to a file.
        mosaicImg.save("mosaic.jpg")

if __name__=="__main__":
        img = Image.open("steve-jobs.jpg")
        imgdir="./image"
        basepath=os.path.join(os.path.abspath('.'),'image')
        print basepath+os.sep
        resolution = (44,50)
        tilesize = (100,100)
        buildMosaic(img, basepath, tilesize, resolution)


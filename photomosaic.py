# @date:	2011-10-10
# @author:	ymeng7
from PIL import Image
import os, sys


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
        w = (int) (origsize[0] * widthFactor) # width of scaled image
        h = (int) (origsize[1] * heightFactor) # height of scaled image
        newimg = Image.new("RGB",(w,h))
        for x in range(w):
                for y in range(h):
                        # transfer pixels according to the scale factors 
                        pxl=origImage.getpixel((((int)(x/widthFactor)),
                        ((int)(y/heightFactor))))
                        newimg.putpixel((x,y),pxl)
        return newimg

# The "putBlock" function takes an image block and a base image
# and a location(a tuple specifying the location the pixel at the
# top-left corner of the image block should be put on the base
# image).
def putBlock(block, destImg, location):
        blocksize = block.size # (width, height) of the image block
        destsize = destImg.size # (width, height) of the base image
        try:
                for x in range(blocksize[0]):
                        for y in range(blocksize[1]):
                                # transfer image pixels from the image block
                                pxl = block.getpixel((x,y))
                                # to the base image!
                                destImg.putpixel((location[0]+x,
                                location[1]+y),pxl)
        except IndexError:
                print "Opsss... index error at: ", (x, y)

# The "average" function takes an image as input and it returns
# a pixel consists of the average color (over all the pixels 
# in the image) of each color channel.
def average(img):
        (r,g,b)=(0,0,0) # initialize a counter to store the red/blue/green values
        size=img.size
        c=0 # row stepper
        try:
                for x in range(size[0]):
                        cnt = 0 # column stepper
                        (rr,gg,bb)=(0,0,0) # intermediate counter to store rgb values
                        for y in range(size[1]):
                                # get and store the rgb values within one row
                                # (column by column)
                                tmp=img.getpixel((x,y))
                                rr += tmp[0]
                                gg += tmp[1]
                                bb += tmp[2]
                                cnt += 1
                        # get and store the average rgb values for that row                        
                        r+=(rr/cnt)
                        g+=(gg/cnt)
                        b+=(bb/cnt)
                        c+=1
                # calculate the overall average rgb value
                r/=c
                g/=c
                b/=c
        except TypeError:
                # in case the given image file is already broken
                return None
        return (r,g,b)

# The "buildTile" function takes an image and a tileSize (a
# tuple specifying width and height) as input and it returns 
# a tile(a tuple consisting of a thumbnail image, together
# with the average color of the thumbnail).
def buildTile(img, tileSize):
        thumbnail = scaleTarget(img,tileSize) # scale the given image
        avg=average(img) # calculate the average color of that image
        if avg != None:
                # if nothing's wrong with that image
                return (thumbnail,avg)
        else:
                return None

#The function "scaleTarget" takes an image and a newSize (a 
# tuple specifying desired width and height) as input and it
# returns an image scaled to the given size.
def scaleTarget(img, newsize):
        origsize = img.size
        px = (newsize[0])/(float)(origsize[0]) # width's scale factor
        py = newsize[1]/ (float)(origsize[1]) # height's scale factor
        newimg = scale(img,px,py)
        return newimg

# The function findBestThumb takes a pixel and a list of tiles as input
# and it returns an image that is the thumbnail of the tile whose average
# color value is nearest the color of the input pixel.
def findBestThumb(pixel, tileList):
        # initialize the best-fit color value to the largest possible value
        lowest = sys.maxint
        bestimg = None # best-fit holder
        for i in range(len(tileList)):
                # find the distance between the average color of current
                # thumbnail and the current pixel who need a thumbnail
                dist = distance(pixel, tileList[i][1])
                if lowest >= dist:
                        # if the there is a better fit, take it!
                        lowest = min(lowest,dist)
                        bestTile = tileList[i]
        return bestTile[0]

# The function "makeTileList" takes a list of image file names (strings)
# and a tile size as input and it returns a list of tiles, whose index
# corresponds to the index of the list of given image files.
def makeTileList(imageFileList, tileSize):
        tileList=[] # create an empty list
        for item in range(len(imageFileList)):
                # build the list of tiles from the list of images
                img = Image.open(imageFileList[item])
                tmp=buildTile(img, tileSize)
                if tmp != None:
                        # if the tile is built successfully, append the tile to the list
                        tileList.append(tmp)
        return tileList

# The function "stitchMosaic" takes an image that is the scaled source
# image for the mosaic and a list of tiles as input, and it returns the
# photo mosaic image.
def stitchMosaic(img, tileList):
        # width and height of the scaled source image
        (width,height) = img.size
        # width and height of the thumbnails
        (thubW,thubH) = (tileList[0][0]).size
        # width and height of the mosaic image
        (imgW,imgH) = (width * thubW , height * thubH)
        # create a new blank image to store the mosaic tiles
        mosaic = Image.new("RGB",(imgW,imgH))
        for w in range(width):
                for h in range(height):
                        # take out a pixel
                        curPxl = img.getpixel((w,h))
                        # and find a thumbnail that best suit this pixel
                        pxlImg = findBestThumb(curPxl,tileList)
                        # then put it onto the mosaic image
                        putBlock(pxlImg, mosaic, (w*thubW,h*thubH))
        return mosaic

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
        img = Image.open("lucky.jpg")
        scaleTarget(img, 100,200) 
        """
        filename = input("Which photo do'ya wanna mess with?")
        img = Image.open(filename)
        imgdir="./image"
        basepath=os.path.join(os.path.abspath('.'),'image')
        resolution = (50,50)
        tilesize = (50,50)
        buildMosaic(img, basepath, tilesize, resolution)
        """

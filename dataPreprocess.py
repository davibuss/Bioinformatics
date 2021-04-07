import xml.etree.ElementTree as ET
from math import floor,ceil,sqrt
from openslide import OpenSlide
from tqdm.notebook import tqdm

def distance(p1,p2):
  distance = sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
  return distance

def getCoordinates(filename,size=128):

  tree = ET.parse(filename)
  root = tree.getroot()
  annotations = root[0]

  coordinateList = []

  for rectangle in annotations:
    coordinates = rectangle[0]
    positions = ["downLeft","downRight","topRight","topLeft"]
    rectangleCoordinates = {}
    
    for i,coordinate in enumerate(coordinates):
      X = float(coordinate.get('X').replace(",","."))
      Y = float(coordinate.get('Y').replace(",","."))

      '''Find the largest rectangle within the original rectangle
      so that the final coordinates will be integers 
      '''

      if positions[i].find("Left"):
        X = ceil(X)
      elif positions[i].find("Right"):
        X = floor(X)

      if positions[i].find("top"):
        Y = floor(Y)
      elif positions[i].find("down"):
        Y = ceil(Y)


      rectangleCoordinates[positions[i]] = {"XY":[X,Y]}
        
    coordinateList.append(rectangleCoordinates)

  rRegionList = []

  for rectangle in coordinateList:
    height = distance(rectangle["topLeft"]["XY"],rectangle["downLeft"]["XY"])
    
    width = distance(rectangle["topLeft"]["XY"],rectangle["topRight"]["XY"])

    xiterations = floor(width/size) 
    yiterations = floor(height/size)
    xInitial = rectangle["topLeft"]["XY"][0]
    yInitial = rectangle["topLeft"]["XY"][1]
      
    for i in range(xiterations):
      x = xInitial + size*i

      for j in range(yiterations):
        y = yInitial + size*j
        rRegionList.append((x,y))

  return rRegionList


#Function that need to be called in the notebook
def getImageTiles(filenameImage,filenameXML,size=128):

  #Getting the appropriate upper left coordinates 
  rRegionList = getCoordinates(filenameXML,size)

  image = OpenSlide(filenameImage)

  regionList = []

  for region in tqdm(rRegionList):
    regionImg = image.read_region(region,0,(size,size))
    regionList.append(regionImg)

  return regionList;
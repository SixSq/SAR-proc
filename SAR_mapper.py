import sys
sys.path.append('/root/.snap/snap-python')
import snappy
from snappy import GPF
from snappy import HashMap
from snappy import (ProductIO, ProductUtils, ProgressMonitor)
from datetime import datetime
jpy = snappy.jpy

imageIO = jpy.get_type('javax.imageio.ImageIO')
File = jpy.get_type('java.io.File')

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import time

import gc


def timestamp():
    return("@SAR_PROC - " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + ' - ')

start_time=time.time()
print(timestamp()+"start processing")

# TODO check with zipped files
s1paths = list(sys.argv[1].split(','))
s1meta = "manifest.safe"

products = []
print(timestamp()+"start reading")
for s1path in s1paths:
    s1prd = "%s.SAFE/%s" % (s1path, s1meta)
    reader = ProductIO.getProductReader("SENTINEL-1")
    product = reader.readProductNodes(s1prd, None)
    products.append(product)

# Extract information about the Sentinel-1 GRD products:

for product in products:

    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    band_names = product.getBandNames()
    print("Product: %s, %d x %d pixels" % (name, width, height))
    print("Bands:   %s" % (list(band_names)))
    band = list(band_names)[0].split('_')[-1]

print(timestamp()+"start subsetting")

WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')
geom = WKTReader().read('POLYGON((-4.51 14.69,-4.477 14.227,-4.076 14.243,-4.054 14.642,-4.51 14.69))')


HashMap = jpy.get_type('java.util.HashMap')
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

parameters = HashMap()

x = 4000
y = 4000
width = 4356
height = 4673

parameters.put('copyMetadata', True)
parameters.put('region',  "%s,%s,%s,%s" % (x, y, width, height))
#parameters.put('geoRegion', geom)


subsets = []

for product in products:
    subset = GPF.createProduct('Subset', parameters, product)
    subsets.append(subset)

#print(timestamp()+"Subset dimension: %d x %d pixels" % (subset.getSceneRasterWidth(), subset.getSceneRasterHeight()))
# print("Subset region: %d " % (subset.getRegion()))

# Step 1: Pre-processing - Calibration
print(timestamp()+"start calibration")

parameters = HashMap()

parameters.put('auxFile', 'Latest Auxiliary File')
parameters.put('outputSigmaBand', True)
parameters.put('selectedPolarisations', band)

calibrates = []

for subset in subsets:
    calibrate = GPF.createProduct('Calibration', parameters, subset)
    calibrates.append(calibrate)

# Step 2: Pre-processing - Speckle filtering

parameters = HashMap()
print(timestamp()+"start Speckle Filtering")

parameters.put('filter', 'Lee')
parameters.put('filterSizeX', 7)
parameters.put('filterSizeY', 7)
parameters.put('dampingFactor', 2)
parameters.put('edgeThreshold', 5000.0)
parameters.put('estimateENL', True)
parameters.put('enl', 1.0)

speckles = []

for calibrate in calibrates:
    speckle = GPF.createProduct('Speckle-Filter', parameters, calibrate)
    speckles.append(speckle)

parrameters = HashMap()
print(timestamp()+"start terrain-correction")

parameters.put('demResamplingMethod', 'NEAREST_NEIGHBOUR')
parameters.put('imgResamplingMethod', 'NEAREST_NEIGHBOUR')
parameters.put('demName', 'SRTM 3Sec')
parameters.put('pixelSpacingInMeter', 10.0)
parameters.put('sourceBands', 'Sigma0_' + band)

terrains = []

for speckle in speckles:
    terrain = GPF.createProduct('Terrain-Correction', parameters, speckle)
    terrains.append(terrain)

parameters = HashMap()
print(timestamp()+"start lineartodb-conversion")

lineartodbs = []

for terrain in terrains:

    lineartodb = GPF.createProduct('linearToFromdB', parameters, terrain)
    lineartodbs.append(lineartodb)


def rot_crop(c, ang):
    rot_c = ndimage.rotate(c, ang)
    lx, ly = rot_c.shape
    crop_rot = rot_c[lx/6:-lx/6, ly/6:-ly/6]
    return(crop_rot)


# TODO Try to use ImageIO instead of pyplot
def printBand(product, band, vmin, vmax):
    print(timestamp()+"start Printing")
    band = product.getBand(band)
    w = band.getRasterWidth()
    h = band.getRasterHeight()

    band_data = np.zeros(w * h, np.float32)
    band.readPixels(0, 0, w, h, band_data)

    band_data.shape = h, w
    name = product.getName()

    plt.imshow(rot_crop(band_data, -10.75), cmap=plt.cm.binary_r, vmin=vmin,
               vmax=vmax)
    plt.axis('off')
    plt.tight_layout(pad=0, w_pad=0, h_pad=0)
    plt.savefig(name + '.png', frameon=False)
    print('Printed!')

def print2(band):
    image = band.createColorIndexedImage(ProgressMonitor.NULL)
    print('image created')
    name = File('snappy_indexed_image.png')
    save = imageIO.write(image,'PNG',name)


for lineartodb in lineartodbs:
    printBand(lineartodb, 'Sigma0_' + band + '_db', -25, 5)
    plt.close()
    gc.collect()
    #print2(lineartodb.getBand('Sigma0_VV_db'))


print(timestamp()+"finish processing - " + str(time.time()-start_time) + "seconds")

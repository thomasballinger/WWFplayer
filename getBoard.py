#
#  General Plan:
#  -get image from webcam
#  -identify playing board (must fit a possible 3D transformation of a plane)
#  -Split into 15x15 array
#  -Identify letters at each location
#
#  Plan until can test using webcam:
#  -be able to identify letters from screenshots
#

from PIL import Image
import numpy
import os
import pylab


def pixelDistance(pix1, pix2):
    return sum(pix1) - sum(pix2)

def getImDictFromImage(image_filename):
    """Finds playing grid in image, returns np.array of grid"""
    im = Image.open(image_filename)
    #im.show()
    width, height = im.size
    l_width = width / 15.0
    # assume that a letter space is square 
    l_height = l_width
    grid_y_offset = 128 # HARDCODED FOR RYAN'S IPHONE
    letter_pics = {}
    arrays = []
    for y in range(15):
        for x in range(15):
            l_left = int(x * width/15.0)
            l_top = int(y * width/15.0 + grid_y_offset)
            l_right = int((x) * width/15.0 + int(l_width))
            l_bottom = int((y) * width/15.0 + int(l_height) + grid_y_offset)
            letter_im = im.crop((l_left, l_top, l_right, l_bottom))
            letter_pics[(x,y)] = letter_im
            # MORE HARDCODING FOR CROPPING HERE!
            cr_letter_im = letter_im.crop((6, 8, letter_im.size[0]-6, letter_im.size[1]-4))
            #sm_letter_im = cr_letter_im.resize((10,10), Image.BILINEAR)
            sm_letter_im = cr_letter_im
            bw_letter_im = sm_letter_im.convert("L")
            #sm_letter_im.show()
            bw_letter_a = numpy.array(bw_letter_im)
            #bw_letter_a = numpy.sum(letter_a[:-1], 2)
            arrays.append(bw_letter_a)
            pylab.imshow(bw_letter_a)

    all_images = numpy.dstack(arrays)

    return all_images.swapaxes(0,2).swapaxes(2,1)

def getTrainingKey(textFile):
    """Simple creation of text files to act as keys."""
    key = []
    lines = open(textFile).read().split('\n')
    for y in range(15):
        for x in range(15):
            key.append(ord(lines[y][x]))
    return key

def numToTile(num):
    letter = chr(num)
    specials = {
            ' ':'<blank>',
            '2':'<DL>',
            '3':'<TL>',
            '5':'<TW>',
            '6':'<TW>',
            }
    return specials.get(letter, letter)

def train(*filenames):
    """Returns a classifier that """
    data = None
    answers = None
    all_images = []
    for filename in filenames:
        print filename
        if not os.path.exists(filename) and os.path.exists(filename+'.code'):
            return False
        keys = getTrainingKey(filename+'.code')
        images = getImDictFromImage(filename)
        this_data = images.reshape(images.shape[0], -1)
        this_answers = numpy.array(keys)
        all_images.extend(images)
        if data is None:
            answers = this_answers
            data = this_data
        else:
            data = numpy.concatenate([data, this_data], 0)
            answers = numpy.concatenate([answers, this_answers], 0)

    print 'image shape', images.shape
    print 'data shape', data.shape
    print 'answers shape', answers.shape

    from scikits.learn import svm
    from scikits.learn.metrics import classification_report
    from scikits.learn.metrics import confusion_matrix
    classifier = svm.SVC()

    divider = 400

    classifier.fit(data[:divider], answers[:divider])


    expected = answers[divider:]
    predicted = classifier.predict(data[divider:])

    print "check:"
    print classifier
    print 'predicted', predicted
    print
    print classification_report(expected, predicted)

    print confusion_matrix(expected, predicted)
    print 'len of all_images:', len(all_images)

    for index, (image, prediction) in enumerate(zip(all_images[divider:], predicted)[:25]):
    #for index, (image, prediction) in enumerate(zip(all_images, answers)[50:75]):
        print index, prediction

        pylab.subplot(5, 5, index+1)
        pylab.imshow(image, cmap=pylab.cm.gray_r)
        pylab.title('Prediction: '+numToTile(prediction))

    pylab.show()

def binarize(image, th=100):
    """Character in forground will be ones, else zeros"""
    off_center_color = numpy.sum(image[2:-2, 2:4])
    print off_center_color
    if off_center_color > th:
        image[image < th] = 0
        image[image >= th] = 1
    else:
        image[image >= th] = th + 1
        image[image < th] = 1
        image[image == th+1] = 0
    pylab.imshow(image)
    pylab.show()
    return 

class Matcher():
    """Trainable match for big letters"""
    def __init__(self, keys, images):
        self.train(keys, images)

    def train(self, keys, images):
        data = zip(keys, images)
        print 'keys', keys
        print 'images', images
        self.examples = {}
        for key, image in data:
            print 'key', key
            if key in self.examples:
                self.examples[key].append(binarize(image))
            else:
                self.examples[key] = [image]
        self.masks = {}
        for key in self.examples:
            self.masks[key] = numpy.sum(self.examples[key], 0) / len(self.examples[key])
            pylab.imshow(self.masks[key])
            pylab.show()

if __name__ == '__main__':
    #train('ryan2.PNG', 'ryan3.PNG')
    key1 = getTrainingKey('ryan2.PNG.code')
    key2 = getTrainingKey('ryan3.PNG.code')
    images1 = getImDictFromImage('ryan2.PNG')
    images2 = getImDictFromImage('ryan3.PNG')
    key = key1 + key2
    images = numpy.concatenate([images1, images2], 0)

    matcher = Matcher(key, images)


    # what I imagine would be useful to the Neural Network:
    #  -the overall background color
    #  -downsampled, thresholded image data
    #
    #

     

from cv2 import cv2, countNonZero, cvtColor
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from numpy.core.umath_tests import inner1d


MIN_MATCH_COUNT = 4


######################################
##### Image Alignment Using Sift #####
######################################

img1 = cv2.imread('input_images/box/AT_Translate_2.png')
img2 = cv2.imread('input_images/box/AT_Translate.png')

img1 = cv2.resize(img1,(800,600))
img2 = cv2.resize(img2,(800,600))
img2_2 = img2


gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)


## (2) Create SIFT object
sift = cv2.xfeatures2d.SIFT_create()

## (3) Create flann matcher
matcher = cv2.FlannBasedMatcher(dict(algorithm = 1, trees = 5), {})

## (4) Detect keypoints and compute keypointer descriptors
kpts1, descs1 = sift.detectAndCompute(gray1,None)
kpts2, descs2 = sift.detectAndCompute(gray2,None)



## (5) knnMatch to get Top2
matches = matcher.knnMatch(descs1, descs2, 2)
# Sort by their distance.
matches = sorted(matches, key = lambda x:x[0].distance)

## (6) Ratio test, to get good matches.
good = [m1 for (m1, m2) in matches if m1.distance < 0.7 * m2.distance]

canvas = img2.copy()


if len(good)>MIN_MATCH_COUNT:

    ## (queryIndex for the small object, trainIndex for the scene )
    src_pts = np.float32([ kpts1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kpts2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    ## find homography matrix in cv2.RANSAC using good match points
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

    h,w = img1.shape[:2]
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts,M)

    cv2.polylines(canvas,[np.int32(dst)],True,(0,255,0),3, cv2.LINE_AA)
else:
    print( "Not enough matches are found - {}/{}".format(len(good),MIN_MATCH_COUNT))


## (8) drawMatches
matched = cv2.drawMatches(img1,kpts1,canvas,kpts2,good,None)#,**draw_params)

## (9) Crop the matched region from scene
h,w = img1.shape[:2]
pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
dst = cv2.perspectiveTransform(pts,M)
perspectiveM = cv2.getPerspectiveTransform(np.float32(dst),pts)
im2_aligned = cv2.warpPerspective(img2,perspectiveM,(w,h))
# im2_aligned = cv2.warpAffine(img,M,(w,h))



########################################
##### Displaying the final results #####
########################################

plt.subplot(121),plt.imshow(img1,cmap = 'gray')
plt.title('Main Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(im2_aligned,cmap = 'gray')
plt.title('Aligned Image'), plt.xticks([]), plt.yticks([])
plt.imshow(im2_aligned),plt.show()

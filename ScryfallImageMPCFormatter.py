# author: Connor Jordan
# date: April 2019

import cv2
import numpy as np
import os
import pathlib

# create image output directory if it doesn't exit already
pathlib.Path("./mpcoutput").mkdir(parents=True, exist_ok=True) 
pathlib.Path("./mpcoutput/unfilled").mkdir(parents=True, exist_ok=True) 

# load template in greyscale 
copyright_template = cv2.imread("./wizardsc.png", cv2.IMREAD_COLOR)
copyright_template = cv2.cvtColor(copyright_template, cv2.COLOR_BGR2GRAY) 

# get all image files in directory
for file in os.listdir("./scryfalloutput/"):
	if os.path.splitext(file)[1] != ".png":
		continue
		
	card_name = os.path.splitext(file)[0]
	
	print("Processing card: "+card_name)

	image = cv2.imread("./scryfalloutput/"+card_name+".png", cv2.IMREAD_COLOR)

	height, width, channels = image.shape
	# print(height)
	# print(width)
	# print(channels)

	# create black background image for mpc
	height_mpc = 1151
	width_mpc = 822
	mpc_formatted_image = np.zeros((height_mpc, width_mpc, 3), np.uint8)

	# center image on black background
	y_offset = int((height_mpc - height) / 2)
	x_offset = int((width_mpc - width) / 2)
	mpc_formatted_image[y_offset:y_offset+height, x_offset:x_offset+width] = image

	# cover the white sections in the corners
	cv2.circle(mpc_formatted_image, (0, 0), 100, (0,0,0), -1)
	cv2.circle(mpc_formatted_image, (width_mpc, 0), 100, (0,0,0), -1)
	cv2.circle(mpc_formatted_image, (0, height_mpc), 100, (0,0,0), -1)
	cv2.circle(mpc_formatted_image, (width_mpc, height_mpc), 100, (0,0,0), -1)

	# cover the copyright information -> could do a *2019 NOT FOR SALE
	# convert image to greyscale for template matching
	img_gray = cv2.cvtColor(mpc_formatted_image, cv2.COLOR_BGR2GRAY) 

	res = cv2.matchTemplate(img_gray, copyright_template, cv2.TM_CCOEFF_NORMED)

	# Store the coordinates of matched area in a numpy array 
	match_location = np.where( res >= 0.6) # tolerance for the match
	temp_width, temp_height = copyright_template.shape[::-1] 

	# cover the matched region with black on the output image
	for pt in zip(*match_location[::-1]):
		if pt[0] < 400: # ignore matches of old formatted copyrights on the left side of the card
			break
		cv2.rectangle(mpc_formatted_image, pt, (pt[0] + temp_width, pt[1] + temp_height), (0,0,0), cv2.FILLED) 

	# numpy_horizontal = np.hstack((image, grey))

	# save image without flood filled boarders (backup)
	cv2.imwrite("./mpcoutput/unfilled/"+card_name+".png", mpc_formatted_image)

	# fill in the border from greyish to black 	# don't fill inside 66- 756
	for x in range(0, 600, 300):
		cv2.floodFill(mpc_formatted_image, None, (110 + x, 65), (0,)*3, (6,)*3, (6,)*3) # (0,)*3, (5,)*3, (5,)*3 = threshold values
		cv2.floodFill(mpc_formatted_image, None, (100 + x, 1075), (0,)*3, (6,)*3, (6,)*3)

	# save image with flood filled boarders
	cv2.imwrite("./mpcoutput/"+card_name+".png", mpc_formatted_image)
	
	# cv2.namedWindow("IMG", cv2.WINDOW_NORMAL)
	# cv2.resizeWindow("IMG", width_mpc, height_mpc)
	# cv2.imshow("IMG", mpc_formatted_image)
	# cv2.waitKey(5000)


	#cv2.destroyAllWindows()




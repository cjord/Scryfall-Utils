# author: Connor Jordan
# date: April 2019

# this script grabs high qualily scans from https://scryfall.com/ using their API
# and saves the images locally to be modified with partner script ScryfallImageMPCFormatter
# this loads lists of cards inputted in the format of https://www.mtggoldfish.com/ output
# or many other Magic the Gathering deck/collection 

import requests
import urllib
import json
import pathlib
import re
import time
import sys

# input file must be formatted 1 card per line
cards_file = open("cards.txt", "r")

# create image output directory if it doesn't exit already
pathlib.Path("./scryfalloutput").mkdir(parents=True, exist_ok=True) 

# output log file
out_file = open("out.txt", "w")

for line in cards_file:
	# parse input
	regex = re.compile(r"^(\d*)?x?([a-zA-Z',\/ \-]*)\[?(\w*).*$")
	matches = regex.findall(line)[0]

	quantity = matches[0]
	card_name = matches[1].strip()
	card_set = matches[2]
	card_name = re.sub("//", "", card_name)
	#print("Card name: " + card_name)
	
	my_file = pathlib.Path("./scryfalloutput/"+card_name+".png")
	if my_file.is_file():
		# command line arg to overwrite exising files
		# default behavior is skip them
		if len(sys.argv) == 1:
			print("Image already found for: "+card_name)
			continue

	# build the url for the api call
	url = "https://api.scryfall.com/cards/search?"
	
	query = card_name
	if len(card_set) > 0:
		query += " set:"+card_set
	
	vars = { "q" : query }
	
	api_url = url + urllib.parse.urlencode(vars)
	#print(api_url)
	
	# make the api request and save resulting json
	res = requests.get(api_url)
	res_json = res.json()
	
	# json object has type list on successful api calls
	if res_json["object"] == "error":
		print("Card not found: "+card_name+" "+card_set)
		
		# could be issue with set not being accurate
		if len(card_set) == 0:
			continue
		else:
			out_file.write("Set not found: "+card_name+" "+card_set+" getting default set image\n")
			vars = { "q" : card_name }
			api_url = url + urllib.parse.urlencode(vars)
			#print(api_url)
			
			# make the api request and save resulting json
			res = requests.get(api_url)
			res_json = res.json()
	
	# multiple matching cards
	index = 0
	if len(res_json["data"]) > 1:
		print("Multiple card matches found, enter index of correct card:")

		for card in res_json["data"]:
			print("Index: "+str(index)+" Name: "+card["name"])
			index += 1
		index = int(input())
		
	# get image urls from json
	img_url = ""
	try:
		img_url = res_json["data"][index]["image_uris"]["png"]
	except:
		# try:
			# # some cards may not have higher quality png image
			# img_url = res_json["data"][0]["image_uris"]["large"]
		# except:
		try:
			# handle dual faced cards 
			# front image
			img_url = res_json["data"][index]["card_faces"][0]["image_uris"]["png"]
			
			img_file = open("./scryfalloutput/"+card_name+" front.png", "wb")
			img_file.write(requests.get(img_url).content)
			
			# back image
			img_url = res_json["data"][index]["card_faces"][1]["image_uris"]["png"]
			
			img_file = open("./scryfalloutput/"+card_name+" back.png", "wb")
			img_file.write(requests.get(img_url).content)
			img_file.close()
			
			# reset img_url so there are no duplicate images loaded
			img_url = ""
		except:
			print("NO IMAGE FOUND")
			out_file.write("No image found: "+card_name+" "+card_set+"\n")
			#out_file.write(json.dumps(res_json, indent=2))
	
	# get the image and save it
	if len(img_url) > 0:
		img_file = open("./scryfalloutput/"+card_name+".png", "wb")
		img_file.write(requests.get(img_url).content)
		img_file.close()
		

	out_file.write("Card saved: "+card_name+" "+card_set+"\n")
	print("Card saved: "+card_name+" "+card_set)
	# wait 100ms to avoid overloading the server with api calls
	time.sleep(0.1)

# files should be closed by the destructor but we close them anyways
out_file.close()
cards_file.close()
	
print()
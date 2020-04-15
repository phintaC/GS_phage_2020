#!/usr/bin/env python3
# create_display_name.py
import sys,os,argparse,csv

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", help="Input file from which to generate display_name")

args = parser.parse_args()

files = args.input

dndict = dict()

for file in files:
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while opening input file: {}\n".format(str(err)))
		sys.exit(1)

	lines = infile.readlines() # Read entire file, small so OK
	infile.close()
	
	row_num = 1
	
	datamatrix = [[] for i in range(len(lines))]
	datamatrix[0] = lines[0].split("\t")
	datamatrix[0].insert(2,"display_name")
	
	for line in lines[1:]:
		datamatrix[row_num] = line.rstrip().split("\t")

		if not datamatrix[row_num][0].startswith("DTU_"):
			datamatrix[row_num].insert(2, dndict[datamatrix[row_num][0]])

		else: 
			display_name = datamatrix[row_num][3] + "-" + datamatrix[row_num][0].split("_")[2] # CTR-NUM
			datamatrix[row_num].insert(2, display_name)

			dndict[datamatrix[row_num][1]] = display_name
		
		row_num += 1


# Write data back to file
try:
	with open(file, "w+") as outfile:
		csvwriter = csv.writer(outfile, delimiter="\t")
		csvwriter.writerows(datamatrix)
except IOError as err:
	sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
	sys.exit(1)

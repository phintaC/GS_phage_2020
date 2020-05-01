#!/usr/bin/env python3
# imgvr_genome_id.py
# Combines the 10 digit genome IDs of IMG/VR database
import sys,os,csv,re

# Provide a small description of usage
if len(sys.argv) != 3:
	sys.stdout.write("Usage: combine_imgvr_id.py <imgvr data file> <taxonoid list>")
	sys.exit(1)

#####################################################################################
# Setup datamatrix
try:
	infile = open(sys.argv[1],"r")
	taxonoidfile = open(sys.argv[2],"r")
except IOError as err:
	sys.stderr.write(str(err))
	sys.exit(1)

data = infile.readlines()

#####################################################################################
# Create set of taxon OIDs
taxonoids = set()
for line in taxonoidfile:
	taxonoids.add(line.rstrip())

#####################################################################################
# Setup matrix
datamatrix = [[] for i in range(len(data))]
header = data[0].rstrip().split("\t")
for i,line in enumerate(data):
	datamatrix[i] = line.rstrip().split("\t")

#####################################################################################
# Setup dict of genome ids and positions
header = datamatrix[0]
id_map = dict()
listnum = 0
for i,item in enumerate(header):
	matchObj = re.findall(r"(\d{8,10})",item)
	if len(matchObj) > 1: 
		count = 0
		for item in matchObj:
			if item in taxonoids:
				count += 1
				if count > 1:
					print("### Warning! Multiple taxon OID annotations for: {}\n".format(header[i]))
				datamatrix[0][i] = item
	elif len(matchObj) == 1:
		datamatrix[0][i] = matchObj[0]

	# Create dict of genome IDs and data points
	if datamatrix[0][i] in id_map:
		id_map[datamatrix[0][i]] += [i]
	else:
		id_map[datamatrix[0][i]] = [i]

#####################################################################################
# Create header row of new matrix
newmatrix = [[] for i in range(len(data))]
for key in id_map:
	newmatrix[0].append(key)

#####################################################################################
# Aggregate data in new matrix
for i,row in enumerate(datamatrix[1:]):
	newmatrix[i+1].append(row[0]) # Annotate sample name
	for j,taxonoid in enumerate(newmatrix[0][1:]): # Omit sample
		newmatrix[i+1].insert(j+1,0)
		for pos in id_map[taxonoid]:
			newmatrix[i+1][j+1] += float(datamatrix[i+1][pos])

#####################################################################################
# Write new matrix to file
outname = os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".taxonoid.tsv"
sys.stdout.write("New file written to: {}\n".format(outname))
sys.stdout.write(">> Number of genome IDs in file: {}\n\
>> Number of UViGs in input file: {}\n\
Dataset reduced with: {:.2f} %\n".format(len(newmatrix[0])-1, len(datamatrix[0])-1,100-(len(newmatrix[0])-1)/(len(datamatrix[0])-1)*100))
try:
	with open(outname, "w+") as csvfile:
		csvwriter = csv.writer(csvfile, delimiter="\t")
		csvwriter.writerows(newmatrix)

except IOError as err:
	sys.stderr.write("Error while opening outfile: {}\n".format(str(err)))
	sys.exit(1)

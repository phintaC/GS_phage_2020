#!/usr/bin/env python3
# group_phage.py
import sys,os,argparse,numpy as np
parser = argparse.ArgumentParser()

parser.add_argument("-i","--input",help="Input file")
parser.add_argument("-g","--group",help="Grouping file",required=True)
parser.add_argument("-t", "--tax", help="Taxonomical level", )

args = parser.parse_args()
###################################################
try:
	infile = open(args.input, "r")
	groupfile = open(args.group,"r")
except IOError as err:
	sys.stderr.write(str(err))
	sys.exit(1)

# Find index of taxon level
grouplines = groupfile.readlines()
header = grouplines[0].rstrip().split()
for i,contents in enumerate(header):
	if "accession" in contents:
		accidx = i
	if args.tax == "species":
		taxclass = "species"
		if "species" in contents:
			idx = i
	if args.tax == "order":
		taxclass = "orders"
		if "order" in contents:
			idx = i
	if args.tax == "family":
		taxclass = "families"	
		if "family" in contents:
			idx = i
	if args.tax == "genus":
		taxclass = "genera"
		if "genus" in contents:
			idx = i
	if args.tax == "host_phylum":
		taxclass = "host phyla"
		if "phylum" in contents:
			idx = i
	if args.tax == "clade":
		taxclass = "clades"
		if "clade" in contents:
			idx = i

# Setup accession : group dict
grpDict = dict()
tax_count = 0
for line in grouplines[1:]: # skip the first line
	line = line.rstrip().split("\t")
	if line[accidx] not in grpDict:
		grpDict[line[accidx]] = line[idx]

# Setup start matrix
inlines = infile.readlines()
accessions = inlines[0].rstrip().split("\t")
datamatrix = [[] for i in range(len(inlines))]
for i,line in enumerate(inlines):
	line = line.rstrip().split("\t")
	datamatrix[i] = line

newmatrix = [[] for i in range(len(datamatrix))]
newmatrix[0].append("sample")
tax_map = dict()
# Map accession number positions to tax level
for i,accession in enumerate(datamatrix[0]):
	if accession[-2] == ".":
		accession = accession[:-2]
	# Setup mapping dict
	if accession in grpDict:
		if grpDict[accession] not in tax_map:
			tax_map[grpDict[accession]] = [i]
			if grpDict[accession] == "Unclassified":
				print("Unclassified phage: " + accession)
		else:
			tax_map[grpDict[accession]] += [i]
			if grpDict[accession] == "Unclassified":
				print("Unclassified phage: " + accession)	
		# Setup header of new matrix
		if grpDict[accession] not in newmatrix[0]:
			newmatrix[0].append(grpDict[accession])
	else:
		if accession != "sample":
			sys.stdout.write("Warning! \"{}\" not found in grouping dict!\n".format(accession))

# Aggregate data in new dict
rownum = 1
col_set = set()
total_num = 0
for i,row in enumerate(datamatrix[1:]): # We don't care about the first row
	newmatrix[i+1].append(row[0]) # Annotate sample name
	
	#
	for j,col in enumerate(newmatrix[0][1:]): # find the tax positions
		newmatrix[i+1].insert(j+1,0) # Fill with zeros
		if col not in col_set:
			sys.stdout.write(">>> Aggregating {} datapoints for {}\n".format(len(tax_map[col]),col))
			total_num += len(tax_map[col])
			col_set.add(col)
			tax_count += 1

		for pos in tax_map[col]:
			newmatrix[i+1][j+1] += float(datamatrix[i+1][pos])
		rownum = -1

npmatrix = np.asmatrix(newmatrix)
#print(npmatrix)

outname = os.path.splitext(os.path.basename(args.input))[0] + "." + taxclass + ".tsv"
np.savetxt(outname,npmatrix,delimiter="\t",newline="\n",fmt="%s")
print("\nWritten to file: {}\n".format(outname))
print("Number of taxonomical {} in the dataset: {}".format(taxclass, tax_count))
print("Total number of phages annotated: {}".format(total_num))
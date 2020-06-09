#!/usr/bin/env python3
#mapstat_results.py
import sys,os

reffiles = sys.argv[2:]
infile_dir = sys.argv[1]

refset = set()
for file in reffiles:
	reffile = open(file, "r")
	if "nuccore" in file: 
		for line in reffile:
			if line.startswith("NC_"):
				refset.add((line.split("\t")[0]).split(".")[0])

	
	elif "taxid10239" in file:
		for line in reffile:
			line = line.rstrip().split("\t")
			if len(line) > 1 and line[1].startswith("NC_"):
				refset.add(line[1].rstrip())

	elif "imgvr" in file:
		reffile.readline() # Skip the first line
		for line in reffile:
			line = line.rstrip().split()
			refset.add(line[0])


os.chdir(infile_dir)
for file in os.listdir(infile_dir):
		
	if os.path.isfile(file):

		outname = os.path.splitext(file)[0] + ".phages.res"
		print("File write to: {}".format(outname))
		outfile = open(outname, "w+")
		
		infile = open(file, "r")
		for line in infile:
			contents = line.rstrip().split("\t")
			if contents[0].startswith("#"):
				outfile.write(line)
		
			if not contents[0].startswith("#"):
				accession = ((contents[0]).split(" ")[0]).split(".")[0]
				if accession in refset:
					outfile.write(line)
#!usr/bin/env python3
import os, sys
# Define extension tuple
fqext = (".fq.gz", ".fastq.gz")

# Prompt for stuff
file_in = input("Please provide csv file of paths for raw files: ")
delim = input("Please specify delimiter (e.g. \",\", \"tab\"...): ")
if delim == "tab":
	delim = "\t"

path_out = input("Please provide replacement path: ")
file_out = input("Name your output csv file: ") + ".csv"

with open(file_out, "w") as outfile:
	outfile.write("")

# Replace paths
with open(file_in, "r") as infile: 
	for line in infile:
		# Splits the columns on delimiter
		r1_col = line.split(delim)[0]
		r2_col = line.split(delim)[1]
		
		# Extracts the file names and replaces extension
		r1_trim = r1_col.split("/")[-1].replace(".fastq.gz", ".trim.fq.gz")
		r2_trim = r2_col.split("/")[-1].replace(".fastq.gz", ".trim.fq.gz")

		# Creates singletons from r1
		singletons = r1_col.split("/")[-1].replace(".fastq.gz", ".singletons.fq.gz")

		# Writes to file
		with open(file_out, "a") as outfile: 
				outfile.write(path_out + r1_trim + "\t" +\
					path_out + r2_trim + "\t" +\
					path_out + singletons + "\n")

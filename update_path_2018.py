#!usr/bin/env python3
import os, sys, re
# Define extension tuple
fqext = (".fq.gz", ".fastq.gz")

# Prompt for stuff
path_out = "/home/projects/cge/backup/fastq/cge_private/FOOD_seqdata/HiSeq/Metagenomics/Trimmed_data/2019_Flowcell_1/"

file_in = "/home/phine/Documents/DTU/thesis/data/unpublished/paths_jun2018.csv"
delim = ","

file_out = input("Name your output csv file: ") + ".csv"

with open(file_out, "w") as outfile:
	outfile.write("")

# Replace paths
with open(file_in, "r") as infile: 
	for line in infile:
		# Splits the columns on delimiter
		r1_col = line.split(delim)[0].rstrip()
		r2_col = line.split(delim)[1].rstrip()
		
		# Extract filename for directory access
		trim_dir = path_out + r1_col.split("/")[-1].replace("_R1.fastq.gz", "_trim/")

		# Extracts the file names and replaces extension
		r1_trim = r1_col.split("/")[-1].replace(".fastq.gz", ".trim.fq.gz")
		r2_trim = r2_col.split("/")[-1].replace(".fastq.gz", ".trim.fq.gz")

		# Creates singletons from r1
		singletons = r1_col.split("/")[-1].replace(".fastq.gz", ".singletons.fq.gz")

		# Writes to file
		with open(file_out, "a") as outfile: 
				outfile.write(trim_dir + r1_trim + "\t" +\
					trim_dir + r2_trim + "\t" +\
					trim_dir + singletons + "\n")

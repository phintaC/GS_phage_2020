#!usr/bin/env python3
import os, sys, re
# Define extension tuple
fqext = (".fq.gz", ".fastq.gz")

# Prompt for stuff
path = "/home/projects/cge/backup/fastq/cge_private/FOOD_seqdata/HiSeq/Metagenomics/Trimmed_data/"

file_in = "/home/phine/Documents/DTU/thesis/data/unpublished/" + input("Please provide csv file of paths for raw files: ")
delim = input("Please specify delimiter (e.g. \",\", \"tab\"...): ")
if delim == "tab":
	delim = "\t"

path_out = "/home/projects/cge/backup/fastq/cge_private/FOOD_seqdata/HiSeq/Metagenomics/Trimmed_data/" + input("Please provide replacement path (from \"/Trimmed_data/\": ")
file_out = input("Name your output csv file: ") + ".csv"

with open(file_out, "w") as outfile:
	outfile.write("")

# Replace paths
with open(file_in, "r") as infile: 
	for line in infile:
		# Splits the columns on delimiter
		r1_col = line.split(delim)[0].rstrip()
		r2_col = line.split(delim)[1].rstrip()
		
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

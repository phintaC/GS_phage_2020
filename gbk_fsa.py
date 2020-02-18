#!usr/bin/env python3
import os,sys

# Changes working directory to file directory 
os.chdir("/home/phine/Documents/DTU/thesis/databases/41586_2020_2007_MOESM6_ESM/genbank_genomes_SD-4")

# Specifies outfile name 
fastaFile_out = "/home/phine/Documents/DTU/thesis/phage_ecosystem_2020.fsa"

# Iterates over files in working directory
for file in os.listdir():	
	if file.endswith(".gbk"):

		# Open and work with files in working directory
		try:
			seq = ""
			seqFlag = False

			with open(file, "r") as infile:
				sys.stdout.write("Processing file: {}\n".format(file))
				header = ">" + os.path.splitext(file)[0]

				for line in infile:
					# Extract sequence using stateful parsing
					if line[:2] == "//":
						seqFlag = False
					if seqFlag:
						seq += line[10:-1].replace(" ", "")
					if line[:6] == "ORIGIN":
						seqFlag = True

				# Write to FASTA file
				with open(fastaFile_out, "a") as outfile:
					outfile.write(header + "\n")
					for i in range(0, len(seq), 60):
						outfile.write(seq[i:i+60] + "\n")


		except IOError as err:
			sys.stderr.write("Error while parsing file: " + str(err))
			sys.exit(1)

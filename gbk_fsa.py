#!usr/bin/env python3
import os,sys,re

# Changes working directory to file directory 
os.chdir("/home/phine/Documents/DTU/thesis/databases/41586_2020_2007_MOESM6_ESM/genbank_genomes_SD-4")
#os.chdir("/home/phine/Documents/DTU/thesis/databases/test")

# Specifies outfile name and resets file
fastaFile_out = "/home/phine/Documents/DTU/thesis/phage_ecosystem_2020.fsa"
outfile = open(fastaFile_out, "w")
outfile.write("")
outfile.close()

# Iterates over files in working directory
for file in os.listdir():
	if file.endswith(".gbk"):

		# Open and work with files in working directory
		try:
			with open(file, "r") as infile:
				sys.stdout.write("Processing file:\t{}\n".format(file))
				seq = ""
				seqFlag = False

				for line in infile:

					# Get reported sequence length
					if line.startswith("LOCUS"):
						reported_len = re.search(r"\s*(\d+)\sbp", line).groups()[0]

					# Setup header
					if line.startswith("ACCESSION"):
						header = ">" +os.path.splitext(file)[0] + " | " + line[12:].rstrip()
					
					# Extract sequence using stateful parsing and write to file
					if line[:2] == "//":
						seqFlag = False

						# Write to file when entire sequence is read
						if int(reported_len) == len(seq):
							with open(fastaFile_out, "a") as outfile:
								outfile.write(header + "\n")
								for i in range(0, len(seq), 60):
									outfile.write(seq[i:i+60] + "\n")
								seq = ""

						# Error handling in case of non-matching lengths
						else: 
							sys.stderr.write("Reported length ({}) does not match length of sequence ({})!\n".format(reported_len, len(seq)))
							sys.exit(1)

					if seqFlag:
						seq += line[10:-1].replace(" ", "")
					if line[:6] == "ORIGIN":
						seqFlag = True


		except AttributeError as err: 
			sys.stderr.write("No sequence length reported for file:\t{}\n".format(file))
			sys.exit(1)

		except IOError as err:
			sys.stderr.write("Error while parsing file: {}\n".format(str(err)))
			sys.exit(1)

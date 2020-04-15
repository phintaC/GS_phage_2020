#!/usr/bin/env python3
# renaming.py
import sys,os,argparse,re,csv

parser = argparse.ArgumentParser()

parser.add_argument("-g", "--geo_file", help="File containing metadata on mapped sample names")
parser.add_argument("-i", "--input", nargs="+", help="Input file to have sample names replaced")

args = parser.parse_args()
###################################################################################
# Setup replacement dict
replacements = dict()
country = dict()
index_new, index_old = None, None

# S
try: 
	with open(args.geo_file, "r") as infile:
		line = infile.readline() # 0: sample name; 1: country_alpha2; 2: country_alpha3; 3: country; 4: continent; 5: comment
		# Metadata lines
		for line in infile:
			contents = line.rstrip().split("\t")

			if "missing" in contents[-1]:
				pass
			elif "excluded" in contents[-1]:
				pass
			elif "remapped" in contents[-1]:
				pass

			else:
				if contents[1] not in replacements:
					replacements[contents[1]] = contents[0]
				else:
					sys.stdout.write("### {} already logged in dict, with value(s): {}\n>>> Overwriting with entry: {}\n".format(contents[1], replacements[contents[1]], contents[0]))
					replacements[contents[1]] = contents[0]

except IOError as err:
	sys.stderr.write("Error while opening geo file: {}\n".format(str(err)))
	sys.exit(1)


#for key,value in replacements.items():
#	print("## Key:\t\t{}\n## Value:\t{}\n".format(key, value))

# Replace old sample names with new
files = args.input

for file in files:
	sys.stdout.write("######### Working on {} #########\n".format(os.path.basename(file)))
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while loading input file: {}\n".format(str(err)))
		sys.exit(1)
	
	# Read entire file to memory
	lines = infile.readlines()
	row_num = 1
	discarded_num = 0
	# Setup datamatrix to store the data
	datamatrix = [[] for i in range(len(lines))]
	# Add the first line of the file to the datamatrix
	datamatrix[0] = lines[0].split("\t")
	
	# a log list to keep track of discarded files
	log = list()

	for line in lines[1:]:
		# Insert the line in the datamatrix as a list of data
		datamatrix[row_num] = line.rstrip().split("\t")

		# Check if the sample name is in the dictionary; if True, replace the name
		if datamatrix[row_num][0] in replacements:
			datamatrix[row_num][0] = replacements[datamatrix[row_num][0]][-1]
			
			# Discard all Negative Control samples
			if "Negative Control" in datamatrix[row_num][0]:
				sys.stdout.write(">>> Discarding negative control: {}...\n".format(datamatrix[row_num][0]))
				log.append("{} negative control discarded...".format(datamatrix[row_num][0]))
				datamatrix.pop(row_num)
				discarded_num += 1
			else:
				row_num += 1

		else:
			# The mapped samples may contain "_R1"
			key = datamatrix[row_num][0].rstrip("R1").rstrip("_")

			if key in replacements:
				
				if replacements[key].startswith("DTU_"):
					datamatrix[row_num][0] = replacements[key]
				else:
					datamatrix[row_num][0] = replacements[key] + "_R1"
				
				# Discard all Negative Control samples
				if "Negative Control" in datamatrix[row_num][0]:
					sys.stdout.write(">>> Discarding negative control: {}...\n".format(datamatrix[row_num][0]))
					log.append("{} negative control discarded...".format(datamatrix[row_num][0]))
					datamatrix.pop(row_num)
					discarded_num += 1
				else:
					row_num += 1
			else:
				sys.stdout.write(">>> Discarding {}...\n".format(datamatrix[row_num][0]))
				log.append("{} discarded...".format(datamatrix[row_num][0]))
				datamatrix.pop(row_num)
				discarded_num += 1


	infile.close()

	# Write discarded samples to a log file
	logname = file.split(".")[0] + ".log"
	if len(log) != 0:
		with open(logname, "w+") as logfile:
			logfile.write("Number of discarded samples: {}\n".format(discarded_num))
			for line in sorted(log):
				logfile.write(line + "\n")


	# Write data back to file
	try:
		with open(file, "w+") as outfile:
			csvwriter = csv.writer(outfile, delimiter="\t")
			csvwriter.writerows(datamatrix)

	except IOError as err:
		sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
		sys.exit(1)

	sys.stdout.write("######### Total number of files discarded: {} #########\n".format(discarded_num))
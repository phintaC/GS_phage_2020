#!/usr/bin/env python3
# concat.py
import sys,os,argparse,csv

#Setup argument parser
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", help="Input files to be concatenated")
parser.add_argument("-s", "--study", help="Study")
parser.add_argument("-o", "--output", help="Output path/filename")

args = parser.parse_args()
#######################################################################################
files = args.input

for file in files:
	# Setup the datamatrix
	if file == files[0]:
		try:
			infile = open(file, "r")
		except IOError as err:
			sys.stderr.write("Error while loading {}: {}".format(os.path.basename(file), str(err)))
			sys.exit(1)
	
		# Setup the initial datamatrix
		lines = infile.readlines()
		row = 0
		datamatrix = [[] for i in range(len(lines))]
		for line in lines:
			line = line.rstrip().split("\t")
			datamatrix[row] = line
			row += 1
	
	# Concatenate contents of remaining files to datamatrix 
	else:
		try:
			infile = open(file, "r")
		except IOError as err:
			sys.stderr.write("Error while loading {}: {}".format(os.path.basename(file), str(err)))
			sys.exit(1)

		lines = infile.readlines()
		row = 0
		for line in lines:
			line = line.rstrip().split("\t")
			
			# Check if samples correspond
			if  line[0] == datamatrix[row][0]:
				datamatrix[row].extend(line[1:])
				row += 1
			else:
				align = row
				while line[0] != datamatrix[align][0]:
#					print("Line[0]:\t{}\ndatamatrix[{}][0]:\t{}\n".format(line[0],align,datamatrix[align][0]))
					align += 1

				datamatrix[align].extend(line[1:])


# Setup output filename
if args.output is None:
#	basedir = "/media/phine/Elements/thesis/data/final/" + args.study + "/"
	basedir = "/media/phine/Backup/thesis/data/final/" + args.study + "/"
	if not os.path.exists(basedir):
		os.mkdir(basedir) 
	typ = os.path.basename(files[0]).split(".")[-2]

	outname = basedir + typ + ".concatenated.csv"
else:
	outname = args.output + ".tsv"
try:
	with open(outname, "w+") as outfile:
		csvwriter = csv.writer(outfile, delimiter="\t")
		csvwriter.writerows(datamatrix)
except IOError as err:
	sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
	sys.exit(1)

sys.stdout.write("Concatenated data file written to: {}\n>>> Contents:\n".format(outname))
for file in files:
	sys.stdout.write(os.path.basename(file) + "\n")
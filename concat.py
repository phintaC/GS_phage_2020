#!/usr/bin/env python3
# concat.py
import sys,os,argparse,csv

#Setup argument parser
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+",help="Input files to be concatenated")
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
		datamatrix = [[]for i in range(len(lines))]
		for line in lines:
			line = line.rstrip().split("\t")
			datamatrix[row] = line
			row += 1
		
		row_len = len(datamatrix[0]) # Initial length of first row
	
	# Concatenate contents of remaining files to datamatrix 
	else:
		try:
			infile = open(file, "r")
		except IOError as err:
			sys.stderr.write("Error while loading {}: {}".format(os.path.basename(file), str(err)))
			sys.exit(1)

		lines = infile.readlines()
		head = lines[0].rstrip().split("\t")
		datamatrix[0].extend(head[1:])
		row_len = len(datamatrix[0]) # reference size
		
		row = 1
		for line in lines[1:]:
			line = line.rstrip().split("\t")
			line_len = len(line)-1
			# Check if samples correspond
			if  line[0] == datamatrix[row][0]:
				datamatrix[row].extend(line[1:])
				row += 1
			else:
				align = 0
				while line[0] != datamatrix[align][0] and align != len(datamatrix)-1:
					align += 1
				

				if align == len(datamatrix)-1 and line[0] != datamatrix[align][0]:  
					sys.stdout.write("Could not locate {}\tfrom\t{}\n>>> Adding {} to frame...\n".format(line[0], os.path.basename(file), line[0]))	
					# Insert the missing sample add leading 0s where there is no data and extend the data with given values
					datamatrix.append([line[0]])
					datamatrix[-1].extend([0 for i in range(len(datamatrix[align])-1)])			
					datamatrix[-1].extend(line[1:])	

				else: 
					if len(datamatrix[align]) == row_len-line_len:
						datamatrix[align].extend(line[1:])

					else:
						sys.stdout.write("\nData missing for {}...\n>>> Adding {} zeros\n".format(line[0], row_len-len(datamatrix[align])-line_len))
						# row_len = entire number of columns, len(datamatrix[align]) = the actual number of columns with data
						# line_len is the length of the current line (from which data needs to be added) 
						datamatrix[align].extend([0 for i in range(row_len-len(datamatrix[align])-line_len)])
						datamatrix[align].extend(line[1:])

# Setup output filename
if args.output is None:
	#basedir = "/media/phine/Elements/thesis/final/" + args.study + "/"
	basedir = "/home/phine/Documents/thesis/final/" + args.study + "/"
	if not os.path.exists(basedir):
		os.mkdir(basedir) 
	typ = os.path.basename(files[0]).split(".")[-2]
	outname = basedir + typ + ".concatenated.csv"
else:
	outname = "/home/phine/Documents/thesis/final/" + args.output + ".csv"

try:
	with open(outname, "w+") as outfile:
		csvwriter = csv.writer(outfile, delimiter="\t")
		csvwriter.writerows(datamatrix)
except IOError as err:
	sys.stderr.write("Error while writing to file: {}\n".format(str(err)))
	sys.exit(1)

sys.stdout.write("\nConcatenated data file written to: {}\n>>> Contents:\n".format(outname))
for file in files:
	sys.stdout.write(os.path.basename(file) + "\n")
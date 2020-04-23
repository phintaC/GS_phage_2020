#!/usr/bin/env python3
#summary.py
import sys,os,argparse,csv

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", help="Input file(s)")
parser.add_argument("-n", "--num_samples", nargs=1, type=int, help="Number of samples", required=True)
parser.add_argument("-o", "--output", help="Output filename")
parser.add_argument("-od", "--output_dir", help="Output directory")

args = parser.parse_args()

files = args.input

###########################################################################################################
# Setup datamatrix
datamatrix = [[] for i in range(args.num_samples[0] + 1)]	
datamatrix[0].append("sample")

lines = list()
###########################################################################################################
# Iterate over files; sum metrics
for file in files:
	sys.stdout.write("# Summarising file:\t{}\n".format(os.path.basename(file)))
	row_num = 0	
	line_num = 0

	# Create column name based on file name
	datamatrix[0].append(os.path.basename(file))
	
	try:
		infile = open(file, "r")
	except IOError as err:
		sys.stderr.write("Error while opening infile: {}\n".format(str(err)))
		sys.exit(1)

	# Discard the first line as these are mapping references
	infile.readline()
	lines = infile.readlines()

	# Iterate over each line to sum numbers
	for line in sorted(lines): # Sorts on sample name
		row_num += 1

		line = line.rstrip().split("\t")

		# Collect all sample names from first file; for now assume it has all samples
		if file == files[0]:
			datamatrix[row_num].append(line[0])

		
		sum_list = [float(i) for i in line[1:]] # Type casting values of list
		
		# Check that we are actually writing the correct sample and sum the values
		if line[0] == datamatrix[row_num][0]:
			datamatrix[row_num].append(sum(sum_list))
		
		else:
			# Align the samples and fill in 0s for datasets with no data for a given sample
			align = row_num
			while line[0] != datamatrix[align][0]:
				datamatrix[align].append(0) 
				align += 1

			datamatrix[align].append(sum(sum_list))

	lines.clear()
	infile.close()

###########################################################################################################
# Set up outfile name
if args.output is None:
	outname = "summary_" + (os.path.basename(args.input[0]).split("_")[-1]).split(".")[0] + ".csv"
else:
	outname = args.output + ".csv"

###########################################################################################################
# Setup output directory
if args.output_dir is not None:
	if args.output_dir.startswith("/home/"):
		outdir = args.output_dir
	else:	
		outdir = os.getcwd() + "/" + args.output_dir

	if not os.path.exists(outdir):
		os.mkdir(outdir)
else: 
	outdir = os.path.dirname(args.input[0]) + "/summary/"
	if not os.path.exists(outdir):
		os.mkdir(outdir)

outname = outdir + outname
sys.stdout.write("Writing \"{}\" to:\t{}\n".format(os.path.basename(outname), outdir))
###########################################################################################################
# Print to file
try:
	with open(outname, "w+") as csvfile:
		csvwriter = csv.writer(csvfile, delimiter="\t")
		csvwriter.writerows(datamatrix)

except IOError as err:
	sys.stderr.write("Error while opening outfile: {}\n".format(str(err)))
	sys.exit(1)

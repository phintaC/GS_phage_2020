#!/usr/bin/env python3
# combine2Matrix.py
import sys,os,argparse
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", help="Input directory containing coverage files")
parser.add_argument("-o", "--output", help="Output directory")

args = parser.parse_args()

os.chdir(args.input)
num_files = 0
for file in os.listdir(args.input):
	if os.path.isfile(file):
		num_files += 1

datamatrix = [[] for i in range(num_files + 1)] # number of files + column names
datamatrix[0].append("sample")

row = 1

for file in os.listdir(args.input):
	if os.path.isfile(file):
		print(">>> Working with file: " + os.path.basename(file))
		
		# Set the first item of a row to be the sample name
		sample = (os.path.splitext(file)[0]).split("_")[-1]
		datamatrix[row].append(sample)
		row += 1

		# Fill with data
		infile = open(file, "r")
		infile.readline() # Skip the first headerline of coverage file
		for line in infile:
			# Add genomes to first row 
			line = line.rstrip().split("\t")
			if line[0] not in datamatrix[0]:
				datamatrix[0].append(line[0])
		infile.close()

coverage,depth = False,False
# Fill data in matrix from files:
header = datamatrix[0]
for file in os.listdir(args.input):
	sample = (os.path.splitext(file)[0]).split("_")[-1]
	
	# determines output name 
	if os.path.splitext(file)[-1] == ".cov" and not coverage and not depth:
		coverage = True
	elif os.path.splitext(file)[-1] == ".depth" and not coverage and not depth:
		depth = True


	infile = open(file, "r")
	infile.readline() # Skip the first line of coverage file
	# Find the corresponding row
	for i,row in enumerate(datamatrix):
		if sample == row[0]:
			# If correct row has been encountered, fill it with 0s
			datamatrix[i][1:] = [0] * (len(header) - len(row))

			# Then fill correct positions with data
			for line in infile:
				line = line.rstrip().split("\t")
				if line[0] in header:
					datamatrix[i][header.index(line[0])] = line[-1]
				else:
					print("Warning: {}".format(line[0]))
	infile.close()

#outfile = open("/media/phine/Elements/thesis/coverage_matrix_imgvr.txt", "w+") 
if coverage:
	outname = args.output + "/" + os.path.basename(file).split("_")[0] + "_coverage_matrix.txt"
elif depth:
	outname = args.output + "/" + os.path.basename(file).split("_")[0] + "_depth_matrix.txt"

print("File written to: " + outname)
outfile = open(outname, "w+")
for row in datamatrix:
	for item in row:
		outfile.write(str(item) + "\t")
	outfile.write("\n")
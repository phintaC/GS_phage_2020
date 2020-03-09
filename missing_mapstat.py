#!usr/bin/env python3
# Missing samples
import sys,os

# Prompt for files etc.
if len(sys.argv) != 3:
	sys.stdout.write("Usage: missing_samples.py <file> <directory>\n")
	sys.exit(1)

else:
	file = sys.argv[1]
	directory = sys.argv[2]

# Setup lists containing filenames in csv and in directory
dir_files,lines = list(),list()
cwd = os.getcwd()

try:
	# Create list of directory files ending with ".mapstat"
	os.chdir(directory)
	for dir_file in os.listdir():
		if dir_file.endswith(".mapstat"):
			dir_files.append(dir_file.split(".")[0])

	sys.stdout.write("Number of mapstat files in directory: {}\n".format(len(dir_files)))

	outfilename = os.path.basename(os.path.dirname(directory)) + "_missing.csv"
	outfile = open(outfilename, "w")
	outfile.write("")

	num_expected = 0
	num_missing = 0

	# Make a new csv file of missing files
	os.chdir(cwd)
	with open(file, "r") as infile: 
		for line in infile: 
			num_expected += 1
			line_split = line.split()
			filename = (line_split[0].split("/")[-1]).split(".")[0]

			if len(dir_files) > 0:
				if not any(filename in dir_file for dir_file in dir_files):
					num_missing += 1
					outfile.write(line)
	
	outfile.close()				 


	outfile.close()
	sys.stdout.write("Number of expected mapstat files: {}\n".format(num_expected))
	sys.stdout.write("Number of missing files: {}\n".format(num_missing))

	if num_missing == num_expected and len(dir_files) != 0:
		sys.stdout.write("Wrong directory searched!\n")

except IOError as err:
	sys.stderr.write("Error while opening file: {}\n".format(err))
	sys.exit(1)
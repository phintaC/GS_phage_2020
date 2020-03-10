#!usr/bin/env python3
import sys,os
# Script checks if logfile is complete; Takes into account that all input files to KMA have produced a mapstat file

if len(sys.argv) != 2:
	sys.stdout.write("Usage: check_log.py <absolute path to mapstat files>")
	sys.exit(1)
else:
	directory = sys.argv[1]

completed = False 
mapstat_count, uncompl_count = 0,0

try: 
	for file in os.listdir(directory):
		if file.endswith(".log"):
			filepath = os.path.join(directory, file)

			with open(filepath, 'r') as infile:

				line = infile.readline()

				while line != "":
					
					if line == "# Closing files\n":
						completed = True
						break

					line = infile.readline()
	
			if not completed:
				uncompl_count += 1
				sys.stdout.write("File not completed:\t{}\n".format(file.split(".")[0] + ".mapstat"))
			#else:
			#	sys.stdout.write("File completed:\t{}\n".format(file.split(".")[0] + ".mapstat"))
		elif file.endswith(".mapstat"):
			mapstat_count += 1

except IOError as err: 
	sys.stderr.write("Error while opening file: {}".format(err))
	sys.exit(1)

sys.stdout.write("Total number of mapstat files in directory:\t{}\n".format(mapstat_count))
sys.stdout.write("Total number of uncompleted mapstat files:\t{}\n".format(uncompl_count))
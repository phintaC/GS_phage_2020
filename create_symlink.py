#!usr/bin/env python3
import sys,os,subprocess

### Local testing ###
#phagegs2020 = "/home/phine/Documents/DTU/thesis/"
#
#csvs = list([#os.path.join(phagegs2020, "data/unpublished/jun2017_new.csv"),\
#os.path.join(phagegs2020, "data/unpublished/new_name_scheme/nov2017_new.csv"),\
#os.path.join(phagegs2020, "data/unpublished/new_name_scheme/jun2018_new.csv"),\
#os.path.join(phagegs2020, "data/unpublished/new_name_scheme/nov2018_new.csv")])
#
#filepath = os.path.join(phagegs2020, "data/test/genomic_20190912")

### Actual paths ###
phagegs2020 = "/home/projects/cge/data/projects/other/bacteriophage_global_sewage_Jan2020/"
filepath = "/home/projects/cge/data/projects/5001/GS_II_kma_output/genomic_20190912" 

csvs = list([#phagegs2020+"/kma/jun2017/jun2017.csv",\
phagegs2020+"kma/nov2017/nov2017_new.csv",\
phagegs2020+"kma/jun2018/jun2018_new.csv",\
phagegs2020+"kma/nov2018/nov2018_new.csv"])

try:
	for csv in csvs:
		link_num, checked, exp_link = 0,0,0
		missing_links = list()
		
		with open(csv, "r") as infile:
			# Specify link directory 
			if os.path.basename(csv) == "jun2017_new.csv":
				link_dir = os.path.join(phagegs2020,"kma/jun2017/output/genomic_20190912/")

			elif os.path.basename(csv) == "nov2017_new.csv":
				link_dir = os.path.join(phagegs2020,"kma/nov2017/output/genomic_20190912/")

			elif os.path.basename(csv) == "jun2018_new.csv":
				link_dir = os.path.join(phagegs2020,"kma/jun2018/output/genomic_20190912/")

			elif os.path.basename(csv) == "nov2018_new.csv":
				link_dir = os.path.join(phagegs2020,"kma/nov2018/output/genomic_20190912/")

			# Find appropriate files
			for line in infile:
				exp_link += 1 # expected link number

				# Extract file name and components thereof
				filename = line.rstrip()
				missing_links.append(filename)

				# Check files in given directory for components
				for file in os.listdir(filepath):
					checked += 1

					if filename in file and file.endswith(".mapstat"):
						subprocess.run(["ln", "-s", os.path.join(filepath, file), os.path.join(link_dir, filename + ".mapstat")])
						link_num += 1
						missing_links.remove(filename)					
					
			# Make final check that number of links correspond to expected number of links, otherwise, inform
			if link_num == exp_link:
				sys.stdout.write("All symbolic links created succesfully for {}!\n".format(os.path.basename(csv)))
			else:
				sys.stdout.write("Number of missing symbolic links ({}): {}\n".format(os.path.basename(csv), exp_link-link_num)) 
				for filename in missing_links:
					sys.stdout.write("Missing link to: {}\n".format(filename))

except IOError as err:
	sys.stderr.write("Error while parsing file: {}\n".format(str(err)))
	sys.exit(1)
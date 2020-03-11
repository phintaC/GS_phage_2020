#!usr/bin/env python3
import sys,os

### Local testing ###
#phagegs2020 = "/home/phine/Documents/DTU/thesis/"
#csvs = list([os.path.join(phagegs2020, "data/unpublished/jun2017.csv"), os.path.join(phagegs2020, "data/unpublished/nov2017.csv"), os.path.join(phagegs2020, "data/unpublished/jun2018.csv"), os.path.join(phagegs2020, "data/unpublished/nov2018.csv")]) 
#filepath = os.path.join(phagegs2020, "data/test/metalResistance_20181113/")
### Actual paths ###
phagegs2020 = "/home/projects/cge/data/projects/other/bacteriophage_global_sewage_Jan2020/"
filepath = "/home/projects/cge/data/projects/5001/GS_II_kma_output/genomic_20190912" 

csvs = list([phagegs2020+"/kma/jun2017/jun2017.csv",\
phagegs2020+"kma/nov2017/nov2017.csv",\
phagegs2020+"kma/jun2018/jun2018.csv",\
phagegs2020+"kma/nov2018/nov2018.csv"])

try:
	for csv in csvs:
		link_num, checked, exp_link = 0,0,0
		found = False
		
		with open(csv, "r") as infile:
			# Specify link directory 
			if os.path.basename(csv) == "jun2017.csv":
				link_dir = phagegs2020+"kma/jun2017/output/genomic_20190912/"

			elif os.path.basename(csv) == "nov2017.csv":
				link_dir = phagegs2020+"kma/nov2017/output/genomic_20190912/"

			elif os.path.basename(csv) == "jun2018.csv":
				link_dir = phagegs2020+"kma/jun2018/output/genomic_20190912/"

			elif os.path.basename(csv) == "nov2018.csv":
				link_dir = phagegs2020+"kma/nov2018/output/genomic_20190912/"

			# Find appropriate files
			for line in infile:
				exp_link += 1 # expected link number

				# Extract file name and components thereof
				filename = (os.path.basename(line.split()[0])).split(".")[0]
				fn_comps = filename.split("_")

				comp = fn_comps[-3] + "_"+ fn_comps[-2] + "_" + fn_comps[-1]

				# Check files in given directory for components
				for file in os.listdir(filepath):
					checked += 1

					if component in file and file.endswith(".mapstat"):
						os.symlink(filepath+file, link_dir+file)
						found = True
						link_num += 1

				if checked == 1063 and not found:
					missing_links.append(filename)
					

			# Make final check that number of links correspond to expected number of links, otherwise, inform
			if link_num == exp_link:
				sys.stdout.write("All symbolic links created succesfully for {}!\n".format(os.path.basename(csv)))
			else:
				sys.stdout.write("Number of missing symbolic links ({}): {}\n".format(os.path.basename(csv), exp_link-link_num)) 
				for filename in missing_links:
					sys.stdout.write("Missing link to: {}".format(filename))

except IOError as err:
	sys.stderr.write("Error while parsing file: {}\n".format(str(err)))
	sys.exit(1)



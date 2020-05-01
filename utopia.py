#!/usr/bin/env python3
# topN.py
import sys,os,argparse,math
import numpy as np
import pandas as pd 

parser = argparse.ArgumentParser(description="Find top N organisms by relative abundance")

parser.add_argument("-u", "--utopia",help="Select to get top 1 %", action="store_true")
parser.add_argument("-t", "--top", type=int, help="Top N to be filtered",required=True)
parser.add_argument("-o", "--output", help="Output")
parser.add_argument("-p", "--percent", help="Select to get top N %", action="store_true")
parser.add_argument("-i", "--input", help="Input file", required=True)
parser.add_argument("-a", "--across", help="Select to get top N (%) across dataset", action="store_true")
parser.add_argument("-n", "--number", help="Number of organisms to be displayed")
if len(sys.argv) == 1:
	parser.print_help()
args = parser.parse_args()

###########################################################################################
###  Read the file as pandas dataframe ### 
print("\n>>> Loading file...")
df = pd.read_csv(args.input, delimiter="\t", header=0, index_col=False) 
df.set_index("sample",inplace=True) # Removes the pandas indexing column

###########################################################################################
### Because why not ### 
if args.utopia:
	print("\n############################################################################################################")
	print("## An imagined community that possesses highly desirable or nearly perfect qualities for its inhabitants! ##")
	print("############################################################################################################\n")
	n = round((len(df.columns)-1)*0.01)
	print(">>> Fetching top 1% across data\nThis corresponds to {} of {}...\n".format(n, len(df.columns)-1))

	# Calculate mean of all abundances across samples
	df_mean = df.mean()
	print(df_mean)

	# Find the top 1% of organisms, report their "accessions"
	df_top = df_mean.nlargest(n)
	row_names = df_top.index.values

	# Find the organism with the largest mean abundance
	df_max = df_mean.idxmax()
	print("Organism with largest mean abundance:\t" + df_max + "\n")
	# Setup outfile name
	if args.output is not None:
		outname = os.getcwd + "/" + args.output + ".top1pct.lst"
	else:
		outname = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top1pct.lst"
	
	print(">>> Writing list to: {}".format(outname))
	np.savetxt(outname,row_names,delimiter="\t",fmt="%s")
	sys.exit(0)

###########################################################################################
###  Find top N species ### 
if not args.percent: 
	n = args.top

	# Sanity check that the number of organisms are not exceeded
	if n >= len(df.index)	:
		print("{} equals or exceeds number of organisms in dataset ({})... Terminating!".format(n,len(df.index)))
		sys.exit(0)


	# Find the N most abundant organisms across dataset (mean value)
	if args.across:
		print("\n>>> Finding top {} of {} organisms across dataset\n".format(args.top,len(df.columns)-1))
		# Calculate mean of all abundances across samples
		df_mean = df.mean()
		df_max = df_mean.idxmax()

		print("Organism with largest mean abundance:\t" + df_max + " \n")

		# Find the top N organisms
		df_top = df_mean.nlargest(n)
		row_names = df_top.index.values	
 		
		# Define output name
		if args.output is None:
			outname = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + ".lst"
		else:
			outname = args.output + "top" + str(args.top) + ".lst"

 	# Find the N most abundant organisms for each sample
	else:
		print("\n>>> Fetching top {} of {} organisms for each sample\n".format(args.top, len(df.columns)-1))
		# Returns top N for each line in an aggregated list 
		df_top = df.apply(pd.Series.nlargest, axis=1,n=n)
		row_names = df_top.columns.tolist() # Not row names, as df is not transposed. 


		# Define output name
		if args.output is None:
			outname = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "_sample.lst"
		else:
			outname = args.output + "top" + str(args.top) + "_sample.lst"

###########################################################################################
### Find top N % of species ### 
elif args.percent:
	n = round((len(df.columns)-1) * (args.top/100))

	# Sanity check that the number of organisms are not exceeded
	if n >= len(df.columns)-1:
		print("{} equals or exceeds number of organisms in dataset ({})... Terminating!".format(n,len(df.columns)-1))
		sys.exit(0)

	# Find the N% most abundant organisms across dataset based on mean
	if args.across:
		print("\n>>> Fetching top {}% across data\nThis corresponds to {} of {} organisms\n".format(args.top,n,len(df.columns)-1))
		# Calculate mean of all abundances across samples
		df_mean = df.mean()
		df_max = df_mean.idxmax()

		print("Organism with largest mean abundance:\t" + df_max + "\n")

		# Find top N across organisms 
		df_top = df_mean.nlargest(n)
		row_names = df_top.index.values

		# Define output name
		if args.output is None:
			outname = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "pct.lst"
		else:
			outname = args.output + ".top" + str(args.top) + "pct.lst"
	

	# Find the N% most abundant organisms across each sample
	else:
		print("\n>>> Fetching top {}% for each sample\nThis corresponds to {} of {} organisms for each sample".format(args.top,n,len(df.columns)-1))
		# Find the top N for each line and make list of accessions of all 
		df_top = df.apply(pd.Series.nlargest, axis=1,n=n)
		row_names = df_top.columns.tolist() # Not row names, as df is not transposed. 

		# Define output name
		if args.output is None:
			outname = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "pct_sample.lst"
		else:
			outname = args.output + ".top" + str(args.top) + "pct_sample.lst"



###########################################################################################
### Write list to file ### 
print(">>> Total number of organisms: {}".format(len(row_names)))
print(">>> Writing list to: {}".format(outname))


# Because IMG/VR homepage requires a comma separated file input to fetch organisms - at least that is what I thought!
if "imgvr" in os.path.basename(args.input):
	taxonOID = set()

	for name in row_names:
		taxonOID.add(name.split("_")[0]) # also denoted "IMG Genome ID"

	row_names = np.array(list(taxonOID))
	np.savetxt(outname,row_names,delimiter=",",newline=",",fmt="%s")
else:
	np.savetxt(outname,row_names,delimiter="\t",fmt="%s")

# Write data of the top N to separate file
# Setup file name
if args.percent:
	if args.across:
		topfile = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "pct.csv"
	else:
		topfile = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "pct_sample.csv"
else:
	if args.across:
		topfile = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + ".csv"
	else:
		topfile = os.getcwd() + "/" + os.path.splitext(args.input.split("/")[-1])[0] + ".top" + str(args.top) + "_sample.csv"

# Open the output file
print(">>> Writing file to: {}".format(topfile))
outfile = open(topfile, "w+")

# Process!
indices = list()
with open(args.input, "r") as infile:
	accessions = set(row_names) # convert row_names to set
	header = infile.readline().split("\t")
	indices.append(0)
	# Capture the index of a top accession number
	for i,item in enumerate(header):
		if item in accessions:
			indices.append(i)

	infile.seek(0)
	for line in infile:
		line = line.rstrip().split("\t")
		for index in indices:
			if index == indices[-1]:
				outfile.write(line[index] + "\n")
			else:	
				outfile.write(line[index] + "\t")
outfile.close()
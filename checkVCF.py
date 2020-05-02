#!/usr/bin/env python3
# checkVCF.py
import sys,os,subprocess

indir = sys.argv[1]
excluded = list()
for file in os.listdir(indir):
	file = indir + file
	if file.endswith(".fq.flt.vcf"):
		line = subprocess.check_output(['tail', '-1',file])

		if not line.startswith(b"#CHROM"):
			sys.stdout.write("Include: {}\n".format(os.path.basename(file)))
		else:
			excluded.append(os.path.basename(file))

print("\n")
for ex in excluded:
	print("### Excluded from phylogenetic analysis: {}".format(ex))

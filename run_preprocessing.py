#!/usr/bin/env python
# coding=utf-8

import os
import sys
import re
import json
import nltk
from clean_ref import clean, remove_punct_tokens
from align_texts import swap_word_pairs


 #Cleaning patterns
datereg = re.compile(r'Dato: (\d{2}.\d{2}.\d{4})')
presidentreg = re.compile(r'President: ([ A-ZÆØÅa-zæøå]+)')
presidentdefreg = re.compile(r'Presidenten:')
contentreg = re.compile(r'\n[iI]nnhold\n')
endreg = re.compile(r'StortingetPostboks')
speakerreg1 = re.compile(r'([ A-ZÆØÅa-zæøå]+) \[[0-9:]+\]:')	#Statsminister Erna Solberg [10:13:34]:
speakerreg2 = re.compile(r'([ A-ZÆØÅa-zæøå]+) \(.+\) \[[0-9:]+\]:')	#Jan Bøhler (Ap) [10:13:34]:

patterns = [datereg, presidentreg, presidentdefreg, contentreg, endreg, speakerreg1, speakerreg2]



if __name__ == "__main__":
	try:
		transfile = sys.argv[1]
		reffile = sys.argv[2]
		outfile = sys.argv[3]
	except IndexError:
		sys.exit("Please provide filenames: run_preprocessing.py transfile reffile outfile")

	if not os.path.exists(transfile):
		sys.exit("Please provide a valid filename for the transfile")
	elif not os.path.exists(reffile):
		sys.exit("Please provide a valid filename for the reffile")
	else:
		with open(transfile, 'r') as trans:
			transjson = json.load(trans)

		with open(reffile, 'r') as ref:
			reftext = ref.read()

	ref_cleaned = clean(reftext, patterns)
	ref_tokenized = nltk.word_tokenize(ref_cleaned)
	ref_tok_nopunct = remove_punct_tokens(ref_tokenized)
	ref_txt_nopunct = ' '.join(ref_tok_nopunct)
	newtrans = swap_word_pairs(transjson, ref_tok_nopunct)

	with open(outfile, 'w') as jsonfile:
		json.dump(newtrans, jsonfile, ensure_ascii=False)
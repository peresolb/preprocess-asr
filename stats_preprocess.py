#!/usr/bin/env python3

import sys
import jiwer
import os
import json
from align_texts import get_paragraphs


try:
	expname = sys.argv[1] # as Google StT json
	goldname = sys.argv[2] # textfile without punctuation
except IndexError:
	sys.exit("Please provide filenames: compare_preprocess.py expfile goldfile")

if not os.path.exists(expname):
	sys.exit("Please provide a valid filename for the expfile")
elif not os.path.exists(goldname):
	sys.exit("Please provide a valid filename for the expfile")
else:
	with open(expname, 'r') as expfile:
		expjson = json.load(expfile)
	with open(goldname, 'r') as goldfile:
		goldtext = goldfile.read()

exptext = ' '.join([x['textstring'] for x in get_paragraphs(expjson)])

exprate = jiwer.wer(goldtext, exptext)

print("WER: %s" % (exprate))

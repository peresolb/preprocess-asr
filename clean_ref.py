#!/usr/bin/env python
# coding=utf-8

import os
import sys
import re
import nltk

def clean(mystring, mypatterns):
	"""Takes a string and some compiled regex patterns and removes regex matches from the string"""
	returnstring = mystring
	for pattern in mypatterns:
		returnstring = pattern.sub(r'', returnstring)
	returnstring = re.sub('\n\n', '', returnstring)
	returnstring = re.sub('\n', ' ', returnstring)
	return returnstring

def remove_punct_tokens(mylist):
	"""Takes a tokenized text and removes punctuation tokens"""
	returnlist = []
	for elem in mylist:
		if not re.match(r'^[^\w\s]', elem):
			returnlist.append(elem)
	return returnlist

def identify_sentend(mylist):
	returnlist = []
	sentdividers = ['!', '?', '.', ':']
	for n in range(len(mylist)):
		token = mylist[n]
		if n == len(mylist)-1:
			returnlist.append(token)
		else:
			nexttoken = mylist[n+1]
			if nexttoken in sentdividers:
				returnlist.append("[endtok]")
			else:
				returnlist.append(token)
	return returnlist

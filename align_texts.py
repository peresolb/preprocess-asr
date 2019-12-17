#!/usr/bin/env python
# coding=utf-8

import nltk
import sys
import os
import re
import jiwer
import json
import csv
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance

#converting transcription json

def get_paragraphs(myjson):
	"""Takes a Google StT json paragraphs file and returns a list of dicts for each
	paragraph with starttime, fulltextlist (list of word dicts with start time and end time),
	textlist (list of words), textstring (textlist in string format) and length (of textlist)
	"""
	returnlist = []
	for par in myjson['paragraphs']:
		starttime = par['startTime']
		fulltextlist = par['words']
		textlist = [elem['text'] for elem in fulltextlist]
		textstring = ' '.join(textlist)
		length = len(textlist)
		mydict = {'startTime': starttime,
		'textlist': textlist, 'textstring': textstring,
		'length': length, 'fulltextlist': fulltextlist}
		returnlist.append(mydict)
	return returnlist


# Search for paragraphs in ref algorithm
def align_words(transdictlist, reflist, leven=False, treshold=0.5):
	"""Takes a list of word dicts from Google StT (such as the fulltextlist
	generated by get_paragraphs()), a list, reflist, of a text presumed to be the
	written version of the transcribed text, and returns a list of dictionaries for
	each word where the words in the two lists are aligned: transword: word from transcription
	, startTime: timecode of start of word, endTime: timecode of end of word, transindex: index
	of transword in transdictlist, refword: word from written version (empty if non is found), 
	refindex: index of word in input list (None if no none is found). if leven=False,
	the script only aligns identical words. If leven=True, it also aligns words with a normalized
	Levenshtein distance below treshold. The script only aligns bigram matches in both texts, and
	does not allow crossing matches."""
	indexed_reflist = [(n,reflist[n]) for n in range(len(reflist))] #index the reflist
	intermediatelist = []
	returnlist = [] #list to be returned
	refstartind = 0
	bigram = [] #list used to temporarily store matches while checking if they are bigram matches
	stoprefindex = 0 #index in reflist where looping should start TODO: rename to something with start?
	for n in range(len(transdictlist)): #loop through transdictlist
		w = transdictlist[n]
		base = {'transword': w['text'], 'confidence': w['confidence'], 'startTime': w['startTime'], 'endTime': w['endTime'],
		'transindex': n, 'refword': '', 'refindex': None} # The entry in returnlist if no match is found
		returnlist.append(base) #appending to returnlist
		mymatch = {'transword': w['text'], 'confidence': w['confidence'], 'startTime': w['startTime'], 'endTime': w['endTime'],
		'transindex': n, 'refword': '', 'refindex': None}  # TODO: find a way to get to get this without copy-paste from base, without base being altered
		for e in range(len(indexed_reflist)): # Loop through the indexed reflist
			if w['text'].lower() == indexed_reflist[e][1].lower() and indexed_reflist[e][0]>stoprefindex: #if identical words are found in both lists
				mymatch['refword'] = indexed_reflist[e][1] 
				mymatch['refindex'] = indexed_reflist[e][0]
				if len(bigram) == 0: #if bigram list is empty
					if n == range(len(transdictlist))[-1]: #if we have reached the end of transdictlist, 
						returnlist = returnlist[:-1]
						returnlist.append(mymatch) #append the match dict to the end of the returnlist
						stoprefindex = mymatch['refindex'] 
					else:
						bigram.append(mymatch) #append match to bigram awaiting further matches
				elif len(bigram) == 1: #if there is a match in bigram
					if bigram[0]['refindex'] == mymatch['refindex']-1 and bigram[0]['transindex'] == mymatch['transindex']-1: #if the previous word is also a match in both lists 
						returnlist = returnlist[:-2] 
						returnlist.append(bigram[0])
						returnlist.append(mymatch) #append both matches to the end of the returnlist
						stoprefindex = mymatch['refindex']
						bigram = [] #empty bigram list
					else: #if not parallell bigram match
						bigram.pop(0) #empty bigram of previous match
						bigram.append(mymatch) #append current match to bigram awaiting awaiting further matches
				break #break loop through reflist
			elif leven == True and normalized_damerau_levenshtein_distance(w['text'], indexed_reflist[e][1]) <= treshold and indexed_reflist[e][0]>stoprefindex: #same as previous ifblock, but with Levenshtein similarity
				mymatch['refword'] = indexed_reflist[e][1]  
				mymatch['refindex'] = indexed_reflist[e][0]
				if len(bigram) == 0: #Copy-paste of the if-block above. TODO: refactor without copy-paste
					if n == range(len(transdictlist))[-1]: 
						returnlist = returnlist[:-1]
						returnlist.append(mymatch)
						stoprefindex = mymatch['refindex']
					else:
						bigram.append(mymatch)
				elif len(bigram) == 1:
					if bigram[0]['refindex'] == mymatch['refindex']-1 and bigram[0]['transindex'] == mymatch['transindex']-1: 
						returnlist = returnlist[:-2]
						returnlist.append(bigram[0])
						returnlist.append(mymatch)
						stoprefindex = mymatch['refindex']
						bigram = []
					else:
						bigram.pop(0)
						bigram.append(mymatch)
				break
	return returnlist

def find_paragraph_pair(trans_json, ref_lst, treshold=0.7): # Fiks dette
	"""Takes a Google StT json file and a written version of the text as input (tokenized as list), and
	identifies portions of the written version that correspond to the paragraphs of the
	transcription, using normalized Levenhstein list comparison. If there is a match under
	the treshold in the two texts, align_words() is run on the matching paragraphs to align the
	words."""
	trans_dict_list = get_paragraphs(trans_json)
	result_dict_list = [] #output list
	for counter_par, elem in enumerate(trans_dict_list): # loop through transcription paragraphs
		print('Reading paragraph %s' % counter_par)
		textlist = elem['textlist']
		fulltextlist = elem['fulltextlist']
		starttime = elem['startTime']
		parlength = elem['length']
		intermediate_results = {'trans': fulltextlist, 'ref': '', 'startTime': starttime, 'dist': 1, 'ref_start_index': 0, 'ref_end_index': 0} #intermediate storage of matches
		for n in range(len(ref_lst)): #loop through written version. TODO: limit the search space to increase efficiency
			window = ref_lst[n:n+parlength] # search window of same length as paragraph in transcription
			dist = normalized_damerau_levenshtein_distance(textlist, window)
			if not dist < treshold: #discard pairs with a distance above treshold
				pass
			elif dist < intermediate_results['dist']: #replace match already in intermediate_results with a new match of lower distance
				intermediate_results['ref'] = window
				intermediate_results['dist'] = dist
		matchwords = align_words(fulltextlist, intermediate_results['ref'], leven=True) #when matching paragraphs are found, align the words in them
		intermediate_results['matches'] = matchwords #store the aligned words. TODO: find a more intuitive way to store these.
		result_dict_list.append(intermediate_results) #append results to output list
	return result_dict_list

def swap_word_pairs(myjson, ref_txt, partreshold=0.7):
	"""Takes a paragraphs dict from a Google StT json file and a written version of the transcribed text,
	and returns a paragraphs dict where the original words are replaced with the words from align_words"""
	returndict = {'paragraphs': []}
	pairslist = find_paragraph_pair(myjson, ref_txt, treshold=partreshold)
	for n in range(len(myjson['paragraphs'])):
		mydict = {'startTime':myjson['paragraphs'][n]['startTime'],'words':[],'id':myjson['paragraphs'][n]['id']}
		for match in pairslist[n]['matches']:
			mytoken = {'endTime': match['endTime'], 'startTime': match['startTime']}
			if match['refword'] == '':
				mytoken['text'] = match['transword']
				mytoken['confidence'] = match['confidence']
			else:
				mytoken['text'] = match['refword']
				mytoken['confidence'] = 1
			mydict['words'].append(mytoken)
		returndict['paragraphs'].append(mydict)
	return returndict
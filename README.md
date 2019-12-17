# Improve ASR transcriptions using manually written records

## About these scripts
This repository contains scripts that align an ASR transcription of speech with
manually written records of the same speech and replaces (presumably) misrecognized
words with words from the manually written records.

These scripts are written by Per Erik Solberg as part of the preprocessing pipeline of
the parliamentary proceedings transcription project at Språkbanken at the National Library
of Norway. In this project, we make detailed orthographic transcriptions of sound files from
proceedings in the Norwegian parliament (Stortinget). Instead of transcribing manually from
scratch, the sound file is automatically transcribed with 
[Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text/), and the transcribers
subsequently correct the automatic transcription. However, there are also written records of the parliamentary proceedings made by staff at Stortinget. Unlike Språkbanken's own transcriptions, 
these are not exact word-by-word transcriptions but are still fairly close to what is said.
We, therefore, replace words from the automatic transcriptions with words from the written records
using these scripts. We do not have sufficient gold-standard data to properly quantify the improvements,
but we get an improvement in the Word Error Rate (WER) from approx. 0.25 to 0.21 on the test text
provided here (see below). transcribers report that the improvements make the manual transcription work significantly easier.

The scripts are tailor-made for this project, so some of the functionality is only relevant to the
task of improving the Google transcriptions of the Norwegian parliamentary proceedings. However,
it should be relatively easy to adapt the scripts to other, similar use cases.


## How the alignment works
The key functions are align_texts.find_paragraph_pair() and align_texts.align_words(). find_paragraph_pair()
loops through the paragraphs of the Google ASR transcription (usually consisting of about a minute of
transcribed speech). For each paragraph, it loops through the manually written record with a window
of the same token length as the ASR paragraph. It calculates the similarities of the paragraph and the windows
using Normalized Levenstein-Damerau (NLD) list comparison. The most similar window is stored as a match, provided
that the NLD distance is below an adjustable threshold.

For each match of ASR paragraphs and written record window, align_words() tries to align the words in the two-word
strings. Two matching words must either be identical or (if leven=True) have a Levenstein distance below a given
threshold. Moreover, matches must come in, at least, sequences of two to be accepted, to avoid over-generating matches
of frequent words. Also, matches cannot cross each other: If a word in the transcription is accepted as a match
in the written records, subsequent matches must occur after the present match in the written records.

align_texts.swap_word_pairs() swap words in the transcription with their matches in the written records.

## Files
- align_texts.py: contains scripts with the core functionality
- clean_ref.py: functions which strip the written records of punctuation and cleans the text if irrelevant material
- run_preprocessing.py: runs the different functions on a Google ASR json file and a text file of the written records,
and produces an output file in the Google ASR json format. It also contains regexes used to clean the written records.
- stats_preprocess.py: Calculates the WER of a transcription in the Google ASR json format, given a gold-standard transcription
- 20171123-095513_wphr.json: A Google ASR transcription of the parliamentary proceedings of 2017.11.23. Used for testing.
- Stortinget-20171123-095513.ref: The manually written proceedings of the parliamentary proceedings of 2017.11.23. Used for testing.
- Stortinget-20171123-095513_manuell.txt: A manual word-to-word transcription of the parliamentary proceedings of 2017.11.23 made
at Språkbanken. Used as gold-standard.
- LICENSE
- README.md

## How to run
- Produced improved transcription: 

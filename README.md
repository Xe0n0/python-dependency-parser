python-dependency-parser
========================

An example dependency parser for NLP, use arc-eager algorithm.

## Requirement
1. libsvm (with python interface)
2. Python NLTK package, now used to draw tree


## Usage
### Parse

`python parser.py --test` to check predict accuracy with d.data

`python parser.py file` to show dependency tree of given sentences from file, format:
	
	word POS-tag
	word POS-tag

sentence should be separated by empty line

It may take seconds for script to load model

### Train

1. `python trainer.py input out` to covert input file to features list, save to output file.
2. use `svm-train` to train features to model

	now suggest params with -c 32 -g 0.5. You may want to try to use lib linear to train features file to model, which is much faster.

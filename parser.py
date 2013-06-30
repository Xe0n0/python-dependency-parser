# -*- coding: utf-8 -*-
# !/usr/bin/env python

from svmutil import *

from trainer import AEMachine, Token
import nltk
import sys, os

sentence = """Influential members of the House Ways and Means Committee introduced legislation that would restrict how the new savings-and-loan bailout agency can raise capital, creating another potential obstacle to the government's sale of sick thrifts."""

svmmodel = svm_load_model("models/d.spell_scaled.model")

def test_once(tokens):
	# print tokens
	machine_control = AEMachine(tokens)
	machine_control.auto_run()

	for t in tokens:
		t.childs = []
		t.father = 0

	try:

		machine_B = parse_tokens(tokens)

	except:
		print 'error'
		return False

	if machine_control.token_top == machine_B.token_top:
		return True

	return False


def run_test():

	count = 0
	matched = 0.0

	with open('data/d.data') as f:
		sentence = []

		line = f.readline()
		while line:

			if not line.strip():

				count += 1
				if test_once(sentence):
					matched += 1

				sentence = []
				print 'sentences count: {}, root matched: {}, rate: {}%'.format(count, matched, float(matched/count) * 100)

			else:
				tokens = line.split()
				tag = tokens[1]
				sentence.append(Token(tokens[0], index=len(sentence)+1, tag=tag, father=tokens[2]))

			line = f.readline()

		if sentence:
			machine = AEMachine(sentence)
			sentence = []
			machine.auto_run()

def parse_tokens(tokens):

	machine = AEMachine(tokens)

	while not machine.should_end():
		# print machine.stack, machine.token_list
		# print machine.state_features()

		label = svm_predict([0], [machine.state_features()], svmmodel)[0][0]

		label = int(label)
		# print label
		if label == 0:
			machine.left_arc()

		elif label == 1:
			machine.right_arc()

		elif label == 2:
			machine.reduce()

		elif label == 3:
			machine.shift()

	return machine

def parse(sentence):
	"""may not work because nltk pos-tag is different from trained data"""
	tagged = nltk.pos_tag(nltk.word_tokenize(sentence))

	tokens = []
	for i, tup in enumerate(tagged):
		t = Token(tup[0], index=i+1, father=0, tag=tup[1])
		tokens.append(t)


	machine = parse_tokens(tokens)
	machine.display()
	# test_once(tokens)

	
def parse_from_file(path):
	with open(path) as f:
		sentence = []

		line = f.readline()
		while line:

			if not line.strip():

				m = parse_tokens(sentence)
				m.display()
				sentence = []

			else:
				tokens = line.split()
				tag = tokens[1]
				sentence.append(Token(tokens[0], index=len(sentence)+1, tag=tag, father=0))

			line = f.readline()

		if sentence:
			m = parse_tokens(sentence)
			m.display()
			sentence = []

if __name__ == '__main__':
	if len(sys.argv) > 1:
		s = sys.argv[1]
		if s == '--test':
			run_test()
		else:
			parse_from_file(s)
	else:
		print """
Usage:
	python parser.py --test to check predict accuracy with d.data
	python parser.py file to show dependency tree of given sentence from file, format:
	
	word POS-tag
	word POS-tag

	sentence should be separated by empty line
"""

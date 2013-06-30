# -*- coding: utf-8 -*-
# !/usr/bin/env python

trainer_output_path = 'features/d.f.data'
trainer_svm_input = 'data/d.data'
# trainer_svm_input = 'sample_input.txt'

import os, sys
import getopt

from nltk.tree import Tree

tag_set = {()}
tag_list = ['PRP$', 'VBG', 'VBD', 'VBN', ',', "''", 'VBP', 'WDT', 'JJ', 'WP',
			 'VBZ', 'DT', '#', 'RP', '$', 'NN', 'FW', 'POS', '.', 'TO', 'PRP', 
			 'RB', '-LRB-', ':', 'NNS', 'NNP', '``', 'WRB', 'CC', 'LS', 'PDT', 
			 'RBS', 'RBR', 'CD', 'EX', 'IN', 'WP$', 'MD', 'NNPS', '-RRB-', 
			 'JJS', 'JJR', 'SYM', 'VB', 'UH']

tag_i = {'PRP$': 0, 'VBG': 1, 'FW': 16, 'VBN': 3, 'POS': 17, "''": 5, 'VBP': 6, 
		'WDT': 7, 'JJ': 8, 'WP': 9, 'VBZ': 10, 'DT': 11, '#': 12, 'RP': 13, 
		'$': 14, 'NN': 15, 'VBD': 2, ',': 4, '.': 18, 'TO': 19, 'PRP': 20, 
		'RB': 21, '-LRB-': 22, ':': 23, 'NNS': 24, 'NNP': 25, '``': 26, 
		'WRB': 27, 'CC': 28, 'LS': 29, 'PDT': 30, 'RBS': 31, 'RBR': 32,
		'CD': 33, 'EX': 34, 'IN': 35, 'WP$': 36, 'MD': 37, 'NNPS': 38,
		'-RRB-': 39, 'JJS': 40, 'JJR': 41, 'SYM': 42, 'VB': 43, 'UH': 44,
		'_MAX': 44, '$#':999}

class AEMachine:
	def __init__(self, token_list):
		self.stack = [Token('$#')]
		self.tokens = token_list[:]
		self.token_list = token_list[:]
		self.token_list.append(Token('#$'))
		self.last_action = None

	def shift(self):
		self.stack.append(self.token_list.pop(0))

	def reduce(self):
		# if self.token_top.tag == '$#':
			# self.shift()
			# return
		self.stack.pop(-1)

	def left_arc(self):
		# if self.token_top.tag == '$#':
			# self.shift()
			# return
		token = self.stack.pop(-1)
		self.token_list[0].insert_child(token)

	def right_arc(self):
		# if self.token_next.tag == '$#':
			# self.left_arc()
			# return
		token = self.token_list.pop(0)
		self.stack[-1].add_child(token)
		self.stack.append(token)

	def token_top():
	    doc = "The token_top property."
	    def fget(self):
	        return self.stack[-1]

	    return locals()
	token_top = property(**token_top())

	def token_next():
	    doc = "The token_next property."
	    def fget(self):
	        return self.token_list[0]

	    return locals()
	token_next = property(**token_next())

	def state_features(self):
		features = {}

		for x in range(-7,3):
			try:
				if x < 0:
					features.update(self.stack[x].features(x))
				else:
					features.update(self.token_list[x].features(x))

			except IndexError:
				# print 'index error'
				pass

		return features

	def should_end(self):
		return self.token_next.code == '#$' and len(self.stack) == 2


	def __has_dependents(self, token):
			for t in self.token_list:
				if t.father == token.index:
					return True

			return False

	def run_once(self):

		if self.token_top.father == self.token_next.index:
			self.left_arc()
			self.last_action = 0

		elif self.token_next.father == self.token_top.index:
			self.right_arc()
			self.last_action = 1

		elif len(self.stack) > 2 and self.stack[-1].father == self.stack[-2].index and not self.__has_dependents(self.stack[-1]):
			self.reduce()
			self.last_action = 2

		else:
			self.shift()
			self.last_action = 3

	def auto_run(self):
		while True:
			# print self.stack, self.token_list[:1]
			# print self.state_features()
			if self.should_end():
					break;

			self.run_once()
				

	def auto_run_with_dump(self, output_path=trainer_output_path):


		with open(output_path, "a") as f:

			while True:

				if self.should_end():
					break;

				features = self.state_features()

				self.run_once()

				f.write('{}'.format(self.last_action))
				for k, v in sorted(features.iteritems()):
					try:
						f.write(' {}:{}'.format(k, v))
					except ValueError:
						f.write(' {}:{}'.format(k, v))

				f.write('\n')

			# print self.stack, self.token_list[:1]
			# print self.state_features()
		# self.display()


	def display(self):
		self.stack[-1].get_nltk_tree().draw()

	def token_of_index(self, i):
		token = self.tokens[i-1]
		if token.index == i:
			return token
		raise KeyError
		return None

class Token:
	def __init__(self, code, index=-1, father=-2, tag='$#'):
		self.code = code
		self.index = index
		self.father = int(father)
		self.father_token = None
		self.tag = tag
		self.childs = []

	def __repr__(self):
		return '{} {} {}:{}'.format(self.code, self.tag, self.index, self.father)

	def add_child(self, token):
		token.father = self.index
		token.father_token = self
		self.childs.append(token)

	def insert_child(self, token):
		token.father = self.index
		token.father_token = self
		self.childs.insert(0, token)

	def non_spell_features(self, prefix):
		if self.code == '#$' or self.code =='$#':
			return []

		if prefix < 0:
			p = (prefix + 7) * 3
			features = {p + 1: tag_i[self.tag]}
			if self.father_token:

				features.update({p + 3: tag_i[self.father_token.tag]})
				if len(self.father_token.childs) > 1:
					for t in self.father_token.childs:
						if t is not self:
							features.update({p + 4: tag_i[t.tag]})
							break

			return features

		elif prefix is 0:

			p = 21

			features = {p + 1: tag_i[self.tag]}

			if len(self.childs) > 0:

				child = self.childs[0]
				features.update({p + 2: tag_i[child.tag]})

			if len(self.childs) > 1:

				child = self.childs[-1]
				features.update({p + 3: tag_i[child.tag]})


			return features

		elif prefix >= 1:
			p = prefix + 24
			return {p: tag_i[self.tag]}

	def features(self, prefix):
		def code2num(code):
			cl = list(code)
			num = 0.0
			for c in cl:
				num += ord(c)
				num /= 100.0
			# num *= 10.0
			return num

		if self.code == '#$' or self.code =='$#':
			return []

		if prefix < 0:
			p = (prefix + 7) * 3
			features = {p: code2num(self.code), p + 1: tag_i[self.tag]}
			if self.father_token:
				# pass
				features.update({p + 3: tag_i[self.father_token.tag]})
			return features

		elif prefix is 0:

			p = 20

			features = {p + 1: code2num(self.code), p + 2: tag_i[self.tag]}

			if len(self.childs) > 0:
				# print self.childs
				child = self.childs[0]
				features.update({p + 3: code2num(child.code), p + 4: tag_i[child.tag]})

			if len(self.childs) > 1:

				child = self.childs[-1]
				features.update({p + 5: code2num(child.code), p + 6: tag_i[child.tag]})

			return features

		elif prefix >= 1:
			p = (prefix - 1) * 2
			return {27 + p: code2num(self.code), 28 + p: tag_i[self.tag]}

	def get_nltk_tree(self):

		child_trees = [c.get_nltk_tree() for c in self.childs]

		t = Tree(self.__repr__(), child_trees)
		return t

	def display(self, prefix=''):
		print '{}({}'.format(prefix, self.code)
		for c in self.childs:
			c.display(prefix+'	')
		print '{})'.format(prefix)


class Trainer:
	
	def __init__(self, input_path=trainer_svm_input, output_path=trainer_output_path, **kwargs):
		self.input_path = input_path
		self.output_path = output_path
		for k, v in kwargs.iteritems():
			setattr(self, k, v)


	def train_from_data(self):
		f = open(self.input_path)

		sentence = []

		line = f.readline()
		while line:

			if not line.strip():
				machine = AEMachine(sentence)
				sentence = []
				machine.auto_run_with_dump(self.output_path)

			else:
				tokens = line.split()
				tag = tokens[1]
				# if not tag in tag_set:
				# 	tag_set.add(tag)
				sentence.append(Token(tokens[0], index=len(sentence)+1, tag=tag, father=tokens[2]))

			line = f.readline()

		if sentence:
			machine = AEMachine(sentence)
			sentence = []
			machine.auto_run_with_dump(self.output_path)
		f.close()



if __name__ == '__main__':
	input_path = sys.argv[1]
	output_path = sys.argv[2]
	f = open(output_path, 'w')
	f.close()
	t = Trainer(input_path, output_path)
	t.train_from_data()


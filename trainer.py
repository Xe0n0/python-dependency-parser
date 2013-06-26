# -*- coding: utf-8 -*-
# !/usr/bin/env python

trainer_output_path = 'trainer_output.txt'
trainer_svm_input = 'sample_input.txt'
from nltk.tree import Tree

class AEMachine:
	def __init__(self, token_list):
		self.stack = [Token('$')]
		self.token_list = token_list[:]
		self.token_list.append(Token('#'))

	def shift(self):
		self.stack.append(self.token_list.pop(0))

	def reduce(self):
		self.stack.pop(-1)

	def left_arc(self):
		token = self.stack.pop(-1)
		self.token_list[0].add_child(token)

	def right_arc(self):
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

	def state_feature():
		features = []
		for x in range(-2,2):
			try:
				if x < 0:
					features.extend(self.stack[x].features)
				else:
					features.extend(self.token_list[x].features)
			except IndexError:
				pass

		return features

	def auto_train(self):
		def has_dependents(token):
			for t in self.token_list:
				if t.father == token.index:
					return True

			return False

		while self.token_next.code is not '#' or len(self.stack) is not 2:

			if self.token_top.father == self.token_next.index:
				self.left_arc()
				# print 'left_arc'

			elif self.token_next.father == self.token_top.index:
				self.right_arc()
				# print 'right_arc'

			elif len(self.stack) > 2 and self.stack[-1].father == self.stack[-2].index and not has_dependents(self.stack[-1]):
				self.reduce()
				# print 'reduce'

			else:
				self.shift()
				# print 'shift'

			print self.stack, self.token_list[:1]
		# self.display()


	def display(self):
		self.stack[-1].get_nltk_tree().draw()

class Token:
	def __init__(self, code, index=-1, father=-2, tag='$'):
		self.code = code
		self.index = index
		self.father = int(father)
		self.tag = tag
		self.childs = []

	def __repr__(self):
		return '{} {}:{}'.format(self.code, self.index, self.father)

	def add_child(self, token):
		self.childs.append(token)

	def features(self, prefix):
		if self.code is '$' or '#':
			return []

		if prefix == -2:
			return [{1: self.code}]
		elif prefix is -1 or 0:
			p = (prefix + 1) * 6
			features = [{p + 2: self.code}, {p + 3: self.tag}]

			if len(self.childs) > 0:

				child = self.childs[0]
				features.extend({p + 4: child.code, p + 5: child.tag})

			if len(self.childs) > 1:

				child = self.childs[-1]
				features.extend({p + 6: child.code, p + 7: child.tag})

			return features

		elif prefix == 1:
			return [{14: self.code, 15: self.tag}]

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
	
	def __init__(self, **kwargs):
		self.input_path = trainer_svm_input
		self.output_path = trainer_output_path
		for k, v in kwargs.iteritems():
			setattr(self, k, v)


	def read_data(self):
		f = open(self.input_path)

		sentence = []

		line = f.readline()
		while line:

			if not line.strip():
				machine = AEMachine(sentence)
				sentence = []
				machine.auto_train()

			else:
				tokens = line.split()
				print tokens
				sentence.append(Token(tokens[0], index=len(sentence)+1, tag=tokens[1], father=tokens[2]))

			line = f.readline()

		if sentence:
			machine = AEMachine(sentence)
			sentence = []
			machine.auto_train()



if __name__ == '__main__':
	t = Trainer()
	t.read_data()
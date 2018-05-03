# This package includes a pipeline class that is designed to accept a sentence and return a list of annotations
#
import os
from pipeUtils import Document
from pipeUtils import Annotation
import itemData
from itemData import get_item_data
import re

from pyConTextNLP import pyConTextGraph


class ConTextPipe:
	def __init__(self, target_rules, context_rules):
		self.targets=get_item_data(target_rules)
		self.modifiers=get_item_data(context_rules)

	def process(self, sentence_annotation, doc_text):
		start_offset= sentence_annotation.start_index;
		sentence_text = doc_text[sentence_annotation.start_index:sentence_annotation.end_index]
		# Process every sentence by adding markup
		sentence_markup = markup_sentence(sentence_text, modifiers=self.modifiers, targets=self.targets)
		annotations = convertMarkupsAnnotations(sentence_markup, start_offset)

		return annotations


def convertMarkupsAnnotations(markups, offset=0):
	annotations=[]
	# print(markups.getXML()) # uncomment for debugging
	nodes = markups.nodes()
	for n in nodes:
		new_ann = Annotation(start_index=offset+n.getSpan()[0], end_index=offset+n.getSpan()[1], type=n.getCategory()[0], ann_id=n.getTagID())
		mods = markups.getModifiers(n)
		if(len(mods) > 0):
			#print(mods) # uncomment for debugging
			for modifier in mods:
				new_ann.attributes[modifier.getCategory()[0]]=modifier.getTagID()

		annotations.append(new_ann)
	return annotations



def markup_sentence(s, modifiers, targets, prune_inactive=True):
	markup = pyConTextGraph.ConTextMarkup()
	markup.setRawText(s)
	markup.cleanText()
	markup.markItems(modifiers, mode="modifier")
	markup.markItems(targets, mode="target")
	markup.pruneMarks()
	markup.dropMarks('Exclusion')
	# apply modifiers to any targets within the modifiers scope
	markup.applyModifiers()
	markup.pruneSelfModifyingRelationships()
	if prune_inactive:
		markup.dropInactiveModifiers()
	return markup
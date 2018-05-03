import codecs
import os


###############################################################################################
###############################################################################################
###############################################################################################
# this class encapsulates all data related to a span (text sequence) annotation
# including the text it "covers" and the type (i.e. "concept") of the annotation
class Annotation(object):
	def __init__(self, start_index=-1, end_index=-1, type='Annotation', spanned_text='', ann_id=0):
		self.ann_id = ann_id
		self.start_index = start_index
		self.end_index = end_index
		self.type = type
		self.spanned_text = spanned_text
		self.linked_document = None
		self.attributes=dict()

	def getSpan(self):
		return (self.start_index, self.end_index)

	def getCategory(self):
		# pyConText graph objects actually expect a list here
		return [self.type]

	def getCoveredText(self, text):
		if(len(text)>=self.end_index and self.start_index<self.end_index):
			coveredText = (text[self.start_index, self.end_index]).replace('\n',' ').replace('\r',''),
			self.spanned_text = coveredText
			return self.spanned_text
		else:
			print("Annotation span error!")
			return None

	def covers(self, ann):
		if self.start_index <= ann.start_index and self.end_index >= ann.end_index:
			return True
		else:
			return False

	def overlaps(self, ann, attributes_to_compare=[]):
		if self.start_index <= ann.start_index and self.end_index >= ann.start_index:
			return self.attributeMatch(ann, attributes_to_compare)
		elif self.start_index >= ann.start_index and self.end_index <= ann.end_index:
			return  self.attributeMatch(ann, attributes_to_compare)
		elif self.start_index <= ann.end_index and self.end_index >= ann.end_index:
			return  self.attributeMatch(ann, attributes_to_compare)
		else:
			return False

	def exactMatch(self, ann, attributes_to_compare=[]):
		if (self.start_index == ann.start_index and
				self.end_index == ann.end_index): # the annotations match
			if len(attributes_to_compare) == 0: # check for featues. zero length means no feature comparison
				return True
			else:
				return self.attributeMatch(ann, attributes_to_compare)
		else:
			return False

	def attributeMatch(self, ann, attributes_to_compare=[]):
		if(len(attributes_to_compare) == 0):
			return True;
		# The two annotations match
		# go through all features and compare them between the two annotations
		matchedFlag = True
		for row in attributes_to_compare:
			# [(A1_type, A1_att_name, A1_att_value),(A2_type, A2_att_name, A2_att_value)]
			# if there is an attribute with the specific value
			a1_att_name = row[0][1]
			a1_att_value= row[0][2]
			a2_att_name = row[1][1]
			a2_att_value= row[1][2]
			if (self.attributes.get(a1_att_name) is not None and ann.attributes.get(a2_att_name) is not None ):
				# both annotations have attributes with values
				if( self.attributes.get(a1_att_name)==a1_att_value and ann.attributes.get(a2_att_name) == a2_att_value):
					matchedFlag = True # attribute values match for this pair of attributes
				elif( self.attributes.get(a1_att_name)!=a1_att_value and ann.attributes.get(a2_att_name) != a2_att_value):
					matchedFlag = True # ann does not have the attribute                    
				else:
					return False # ann does not have the attributereturn False # ann does not have the attribute
			elif (self.attributes.get(a1_att_name) is None and ann.attributes.get(a2_att_name) is None ):
				matchedFlag = True  # both blank is a match
			elif (self.attributes.get(a1_att_name) is None and ann.attributes.get(a2_att_name) is not None ):
				if(ann.attributes.get(a2_att_name) == a2_att_value):
					return False # self does not have the attribute
				else:
					matchedFlag=True
			elif (self.attributes.get(a1_att_name) is not None and ann.attributes.get(a2_att_name) is None ):
				if(self.attributes.get(a1_att_name) == a1_att_value):
					return False # self does not have the attribute
				else:
					matchedFlag=True
		return matchedFlag

	def toString(self, doc_text=''):
		line = str(self.ann_id)
		attrs = ''
		for key in self.attributes.keys():
			att = ''
			if isinstance(self.attributes.get(key), Annotation):
				att = self.attributes.get(key).spanned_text
			else:
				att = str(self.attributes.get(key))
			attrs = attrs + '[' + key + ':' + att +']'
		line = line + ' ' + str(self.type)
		line = line + ' ' + str(self.start_index)
		line = line + ' ' + str(self.end_index)
		if self.spanned_text == '':
			if len(doc_text)>self.end_index:
				self.spanned_text = doc_text[self.start_index: self.end_index]
		line = line + ' ' + self.spanned_text
		line = line + ' ' + attrs
		return line

###############################################################################################
###############################################################################################
###############################################################################################

# this class encapsulates all data for a document which has been annotated_doc_map
# this includes the original text, its annotations and also
class Document(object):
	def __init__(self, document_id=-1, text=''):
		self.document_id = document_id
		self.text = text
		self.annotations = []
		self.attributes = dict()

	def load_document_from_file(self, filename):
		f1 = codecs.open(filename, encoding='utf-8')
		self.text = f1.read()
		self.document_id = os.path.basename(filename)
		f1.close()

	def load_annotations_from_brat(self, filename):
		f = open(filename, "r")
		annList = []
		for line in f:
			annList.append(line.strip())
		self.annotations=read_brat_annotations(annList)

	def toString(self):
		line = ''
		delimiter = '\r\n-------\r\n'
		for a in self.annotations:
			line = line + a.toString(self.text)+ '\r\n'
		return str(self.document_id) + delimiter+ self.text + delimiter +line

	def compare_types_by_span(self, ref_type ='Annotation', sys_type='Annotation', exact=True):
		tp, fp, fn = 0,0,0
		tp_list = []
		fp_list = []
		fn_list = []
		ref_anns = []
		sys_anns = []

		# Split annotations of different types into two lists
		for a in self.annotations:
			if(a.type == ref_type):
				ref_anns.append(a)
		for a in self.annotations:
			if(a.type == sys_type):
				sys_anns.append(a)

		# Count tp and fp
		for sys_ann in sys_anns:
			tp_flag = False
			matching_ref = None
			for ref_ann in ref_anns:
				if exact:
					if(sys_ann.exactMatch(ref_ann)):
						tp_flag=True
						matching_ref = ref_ann
				else:
					if sys_ann.overlaps(ref_ann):
						tp_flag = True
						matching_ref = ref_ann
			if tp_flag:
				tp = tp + 1
				tp_list.append([sys_ann, matching_ref])
			else:
				fp = fp + 1
				fp_list.append(sys_ann)

		# Count fn
		for ref_ann in ref_anns:
			tp_flag = False
			for sys_ann in sys_anns:
				if exact:
					if(ref_ann.exactMatch(sys_ann)):
						tp_flag=True
				else:
					if ref_ann.overlaps(sys_ann):
						tp_flag = True
			if not tp_flag:
				fn = fn + 1
				fn_list.append(ref_ann)

		return tp, fp, fn, tp_list, fp_list, fn_list
    
	def compare_types_by_span_and_attributes(self, ref_type ='Annotation', sys_type='Annotation', attributes_to_compare=[] , exact=True):
		tp, fp, fn = 0,0,0
		tp_list = []
		fp_list = []
		fn_list = []
		ref_anns = []
		sys_anns = []
		if len(attributes_to_compare) == 0:
			return self.compare_types_by_span(ref_type, sys_type,exact)
  
		# Split annotations of different types into two lists
		for a in self.annotations:
			if(a.type == ref_type):
				ref_anns.append(a)
		for a in self.annotations:
			if(a.type == sys_type):
				sys_anns.append(a)

		# Count tp and fp
		for sys_ann in sys_anns:
			tp_flag = False
			matching_ref = None
			for ref_ann in ref_anns:
				if exact:
					if(sys_ann.exactMatch(ref_ann, attributes_to_compare)):
						tp_flag=True
						matching_ref = ref_ann
				else:
					if sys_ann.overlaps(ref_ann, attributes_to_compare):
						tp_flag = True
						matching_ref = ref_ann
			if tp_flag:
				tp = tp + 1
				tp_list.append([sys_ann, matching_ref])
			else:
				fp = fp + 1
				fp_list.append(sys_ann)

		# Count fn
		for ref_ann in ref_anns:
			tp_flag = False
			for sys_ann in sys_anns:
				if exact:
					if(ref_ann.exactMatch(sys_ann, attributes_to_compare)):
						tp_flag=True
				else:
					if ref_ann.overlaps(sys_ann, attributes_to_compare):
						tp_flag = True
			if not tp_flag:
				fn = fn + 1
				fn_list.append(ref_ann)

		return tp, fp, fn, tp_list, fp_list, fn_list

###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################

def read_brat_annotations(lines):
	annotations = []
	# BRAT FORMAT is:
	#  A_NUMBER[TAB]TYPE[SPACE]START_INDEX[SPACE]END_INDEX[TAB]SPANNED_TEXT
	#  A_NUMBER[TAB]TYPE[SPACE]START_INDEX[SPACE]END_INDEX;START_INDEX[SPACE]END_INDEX[TAB]SPANNED_TEXT
	# Load annotations
	for line in lines:
		line = str(line)
		if(line.startswith('T')):
			tab_tokens = line.split('\t') # split id, Type & Spans, Spanned_Text
			ann_id = tab_tokens[0]  # first item is the ann_id
			spanned_text = tab_tokens[-1]  #last item is the spanned text
			space_tokens = tab_tokens[1].split()
			ann_type = space_tokens[0]
			ann_span_start = int(space_tokens[1])
			ann_span_end = int(space_tokens[-1])
			anno = Annotation(ann_span_start,ann_span_end,ann_type)
			anno.ann_id=ann_id
			anno.spanned_text=spanned_text.replace('\s', ' ')
			annotations.append(anno)
		elif line.startswith('A'):
			# Load attributes
			tab_tokens=line.split('\t') # split id, Type & ann_id & Attr_Value
			attr_id = tab_tokens[0]
			space_tokens=tab_tokens[1].split(' ')
			attr_type = space_tokens[0].strip(' ')
			attr_arg = space_tokens[1].strip(' ')
			if len(space_tokens) > 2:
				attr_value = space_tokens[2].strip(' ')
			else:
				attr_type = 'True'
			found = False
			for a in annotations:
				if a.ann_id == attr_arg:
					a.attributes[attr_type] = attr_value
					found=True
		elif line.startswith('R'):
			#load relationships
			# R2
			tab_tokens = line.split('\t') # split id, Type & args
			space_tokens = tab_tokens[1].split(' ') # Type, Arg1:T4 , Arg2:T3
			rel_id = tab_tokens[0]
			rel_type = space_tokens[0]
			arg1 = space_tokens[1].split(':')[1]
			arg2 = space_tokens[2].split(':')[1]
			a1 = None
			a2 = None
			for a in annotations:
				if a.ann_id == arg1:
					a1 = a
				if a.ann_id == arg2:
					a2  = a
			if a1 is not None:
				if a2 is not None:
					a1.attributes[rel_type]=a2

	return annotations

def brat_annotations_to_string(annotations):
	curr_id=0
	lines = [] # lines is a list of strings that can be written to file
	for a in annotations:
		if(a.ann_id == 0):
			ann_id = 'T' + str(curr_id)
			a.ann_id = ann_id
			curr_id =+ 1
		line = a.ann_id + '\t' + a.type + ' ' + str(a.start_index) + ' ' + str(a.end_index) + ' ' + a.spanned_text
		lines.append(line)
	return lines



###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################


# pipeUtils

pipeUtils is a simple framework for simple NLP pipelines

## Classes and functions

### Annotation

    from pipeUtils import Annotation
    
    ann1 = Annotation(start_index = 1, end_index = 10, type='Fever')
    ann2 = Annotation(start_index = 12, end_index = 15, type='Temperature')
    ann3 = Annotation(start_index = 20, end_index = 25, type='Value')
    
#### Attributes

 - ann_id - Annotation identifier. Can be left blank.
 - start_index - span starting index. Default -1
 - end_index - span ending index. Default -1
 - type - Annotation type. Default "Annotation"
 - attributes - Dictionary for annotation attributes. Attribute name is the key and value is the attribute value.
 
#### Methods

 - ann1.covers(ann2) - Returns True if annotation 1 covers annotation 2
 - ann1.overlaps(ann2) - Returns True if annotation 1 overlaps with annotation 2
 - ann1.exactMatch(ann2) - Returns True if the span of annotation 1 exactly matches span of annotation 2

### Document

    from pipeUtils import Document
    doc1 = Document(text='This is the document text')

#### Attributes
 - document_id - Document identifier
 - text - Document text
 - annotations - list of annotations
 - attributes - Dictionary for document attributes. Attribute name is the key and value is the attribute value.
 
#### Methods

- doc.load_document_from_file(filename) - loads document text into the Document object from a file
- doc.load_annotations_from_brat(filename) - loads annotaiton from file in brat format
- doc.compare_types_by_span('AnnotationType1', 'AnnotationType2', exact=False) - Returns three integers TP, FP, FN for the document. If exact=True, then true positive requires exact match. If exact = False, then overlap is counted as match.
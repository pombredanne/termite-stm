#!/usr/bin/env python

import os
import json
import urllib
import cStringIO
from utils.UnicodeIO import UnicodeReader, UnicodeWriter
from db.Corpus_DB import Corpus_DB

class Home_Core(object):
	def __init__(self, request, response):
		self.request = request
		self.response = response
		self.configs = self.GetConfigs()
		self.params = {}
		self.content = {}   # All variables returned by an API call
		self.table = []     # Primary variable returned by an API call as rows of records
		self.header = []    # Header for primary variable

################################################################################		
# Server, Dataset, Model, and Attribute

	EXCLUDED_FOLDERS = frozenset( [ 'admin', 'examples', 'welcome', 'init', 'data' ] )
	def IsExcluded( self, folder ):
		if folder in Home_Core.EXCLUDED_FOLDERS:
			return True
		if folder[:5] == 'temp_':
			return True
		return False

	def GetServer( self ):
		return self.request.env['HTTP_HOST']

	def GetDataset( self ):
		return self.request.application

	def GetModel( self ):
		return self.request.controller

	def GetAttribute( self ):
		return self.request.function
	
	def GetURL( self ):
		return self.request.env['wsgi_url_scheme'] + '://' + self.request.env['HTTP_HOST'] + self.request.env['PATH_INFO']
	
	def GetQueryString( self, keysAndValues = {} ):
	   	query = { key : self.request.vars[ key ] for key in self.request.vars }
		query.update( keysAndValues )
		for key in query.keys():
			if query[ key ] is None:
				del query[ key ]
		if len(query) > 0:
			return '?' + urllib.urlencode(query)
		else:
			return ''

	def GetDatasets( self ):
		folders = []
		applications_path = '{}/applications'.format( self.request.env['applications_parent'] )
		for folder in os.listdir( applications_path ):
			if not self.IsExcluded(folder):
				applications_subpath = '{}/{}'.format( applications_path, folder )
				if os.path.isdir( applications_subpath ):
					folders.append( folder )
		folders = sorted( folders )
		return folders
	
	def GetModels( self, dataset ):
		if self.IsExcluded(dataset):
			return None
		folders = []
		with Corpus_DB() as corpus_db:
			folders += corpus_db.GetModels()
		folders = sorted( folders )
		return folders
	
	def GetAttributes( self, dataset, model ):
		if self.IsExcluded(dataset):
			return None
		if model == 'default':
			return None
		if model == 'lda':
			return [
				'DocIndex',
				'TermIndex',
				'TopicIndex',
				'TermTopicMatrix',
				'DocTopicMatrix',
				'TopicCooccurrences',
				'TopicCovariance',
				'TopTerms',
				'TopDocs'
			]
		if model == 'itm':
			return [
				'Update',
				'gib'
			]
		if model == 'corpus':
			return [
				'DocumentByIndex',
				'DocumentById',
				'SearchDocuments',
				'TermFreqs',
				'TermProbs',
				'TermCoFreqs',
				'TermCoProbs',
				'TermPMI',
				'TermG2',
				'SentenceCoFreqs',
				'SentenceCoProbs',
				'SentencePMI',
				'SentenceG2'
			]
		return []
	
	def GetConfigs( self ):
		server = self.GetServer()
		dataset = self.GetDataset()
		datasets = self.GetDatasets()
		model = self.GetModel()
		models = self.GetModels( dataset )
		attribute = self.GetAttribute()
		attributes = self.GetAttributes( dataset, model )
		url = self.GetURL()
		configs = {
			'server' : server,
			'dataset' : dataset,
			'datasets' : datasets,
			'model' : model,
			'models' : models,
			'attribute' : attribute,
			'attributes' : attributes,
			'url' : url,
			'is_text' : self.IsTextFormat(),
			'is_graph' : self.IsGraphFormat(),
			'is_json' : self.IsJsonFormat(),
			'is_csv' : self.IsCSVFormat(),
			'is_tsv' : self.IsTSVFormat()
		}
		return configs
	
################################################################################
# Parameters

	def GetStringParam( self, key ):
		if key in self.request.vars:
			return unicode( self.request.vars[key] )
		else:
			return u''
		
	def GetNonNegativeIntegerParam( self, key, defaultValue ):
		try:
			n = int( self.request.vars[ key ] )
			if n >= 0:
				return n
			else:
				return 0
		except:
			return defaultValue

	def GetNonNegativeFloatParam( self, key, defaultValue ):
		try:
			n = float( self.request.vars[ key ] )
			if n >= 0:
				return n
			else:
				return 0.0
		except:
			return defaultValue
	
################################################################################
# Generate a response

	def IsDebugMode( self ):
		return 'debug' in self.request.vars
	
	def IsTextFormat( self ):
		return not self.IsGraphFormat() and not self.IsJsonFormat()
	
	def IsGraphFormat( self ):
		return 'format' in self.request.vars and 'graph' == self.request.vars['format'].lower()

	def IsJsonFormat( self ):
		return 'format' in self.request.vars and 'json' == self.request.vars['format'].lower()

	def IsCSVFormat( self ):
		return 'format' in self.request.vars and 'csv' == self.request.vars['format'].lower()
	
	def IsTSVFormat( self ):
		return 'format' in self.request.vars and 'tsv' == self.request.vars['format'].lower()
	
	def IsMachineFormat( self ):
		return self.IsJsonFormat() or self.IsGraphFormat() or self.IsCSVFormat() or self.IsTSVFormat()
	
	def HasAllowedOrigin( self ):
		return 'origin' in self.request.vars
	
	def GetAllowedOrigin( self ):
		return self.request.vars['origin']
	
	def GenerateResponse( self ):
		if self.IsDebugMode():
			return self.GenerateDebugResponse()
		else:
			return self.GenerateNormalResponse()
	
	def GenerateDebugResponse( self ):
		envObject = self.request.env
		envJSON = {}
		for key in envObject:
			value = envObject[ key ]
			if isinstance( value, dict ) or \
			   isinstance( value, list ) or isinstance( value, tuple ) or \
			   isinstance( value, str ) or isinstance( value, unicode ) or \
			   isinstance( value, int ) or isinstance( value, long ) or isinstance( value, float ) or \
			   value is None or value is True or value is False:
				envJSON[ key ] = value
			else:
				envJSON[ key ] = 'Value not JSON-serializable'
		
		data = {
			'env' : envJSON,
			'cookies' : self.request.cookies,
			'vars' : self.request.vars,
			'get_vars' : self.request.get_vars,
			'post_vars' : self.request.post_vars,
			'folder' : self.request.folder,
			'application' : self.request.application,
			'controller' : self.request.controller,
			'function' : self.request.function,
			'args' : self.request.args,
			'extension' : self.request.extension,
			'now' : str( self.request.now ),
			'configs' : self.configs,
			'params' : self.params
		}
		data.update( self.content )
		dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		self.response.headers['Content-Type'] = 'application/json'
		return dataStr

	def GenerateNormalResponse( self ):
		data = {
			'configs' : self.configs,
			'params' : self.params
		}
		data.update( self.content )

		if self.IsJsonFormat():
			self.response.headers['Content-Type'] = 'application/json'
			if self.HasAllowedOrigin():
				self.response.headers['Access-Control-Allow-Origin'] = self.GetAllowedOrigin()
			return json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )

		if self.IsCSVFormat():
			f = cStringIO.StringIO()
			writer = UnicodeWriter(f)
			writer.writerow( [ d['name'] for d in self.header ] )
			for record in self.table:
				row = [ record[d['name']] for d in self.header ]
				writer.writerow(row)
			dataStr = f.getvalue()
			f.close()
			self.response.headers['Content-Type'] = 'text/csv; charset=utf-8'
			if self.HasAllowedOrigin():
				self.response.headers['Access-Control-Allow-Origin'] = self.GetAllowedOrigin()
			return dataStr
		
		if self.IsTSVFormat():
			headerStr = u'\t'.join( d['name'] for d in self.header )
			rowStrs = []
			for record in self.table:
				rowStrs.append( u'\t'.join( u'{}'.format( record[d['name']]) for d in self.header ) )
			tableStr = u'\n'.join(rowStrs)
			dataStr = u'{}\n{}\n'.format( headerStr, tableStr ).encode('utf-8')
			self.response.headers['Content-Type'] = 'text/tab-separated-values; charset=utf-8'
			if self.HasAllowedOrigin():
				self.response.headers['Access-Control-Allow-Origin'] = self.GetAllowedOrigin()
			return dataStr
	
		self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
		data['content'] = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
		return data

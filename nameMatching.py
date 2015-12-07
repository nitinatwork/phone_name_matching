'''
Created on Jun 6, 2012

@author: nitin.agarwal


	
'''


import re
import csv
from master_data import DATA as MASTER_DATA
from crawled_data import DATA as CRAWLED_DATA


# 'Similar Phonetics' are words which sound similar. These are language and location dependent.
# A lot can be done to generate these phonetic words using machine learning
# Right now for this solution I am writing phonetics manually.
# These are few examples, we can always add as many as we want.
PHONETICS = {'c' : 'k', 'i' : 'e'}
PHONETICS_DISTANCE = 0.5

CONFFIG = {
			'MAX_WORD_MATCHING_ERROR' : 20, # if two words match 80% it will be considered as matched (Nokia and Nakia will be matched)
			'MAX_ALPHANUMBER_WORD_MATCHING_ERROR' : 10, # if two alphanumber words match 90% it will be considered as matched, in most cases it will be a code
			'MIN_MATCH_IN_PRODUCT_CODE_MODE' : 50, # 50% of each words should match in case of 
			'MIN_MATCH_IN_NORMAL_MODE' : 80
		 }


class ProductNameMatching:
	def __init__(self, type = None):
		self.type = type
		self.master_data = MASTER_DATA
		self.crawled_data = CRAWLED_DATA
		self.output_solution = []
		self._preprocessing_master_data()

	def _preprocessing_master_data(self):
		self.index_product_code()
		self.get_most_comman_word()

	def index_product_code(self):
		self.indexed_product_code = {}
		for key in self.master_data:
			code = self.get_product_name_code(self.master_data[key])
			if code == '':
				continue
			if not self.indexed_product_code.get(code):
				self.indexed_product_code[code] = []
			self.indexed_product_code[code].append(key)


	## part of the name which contains numeric or single 
	## character value will be considered as code
	def get_product_name_code(self, name):
		code = ''
#		print re.sub('[^A-Za-z0-9\s+]+', '', name)
		name_arr = self._filter_name(name).split(' ')
		for val in name_arr:
			if re.search('\d', val) or len(val) == 1:
				code = ''.join([code, val])
#		print name, name_arr, code
		return code
	
	
	
	def _filter_name(self, name):
		## convert to lower case
		name = name.lower()
		## remove special characters like '-,_,@'
		name = re.sub('[^A-Za-z0-9\s+]+', '', name)
		## replace multiple spaces to single space
		return re.sub(' +',' ',name)
		
	'''
	For optimisation Master Data could be converted into a B-Tree
	for example: Nokia -> c2, c3 -> (10, 11), (20, 21)
	Due to time constraints only constructing a order 1 B-tree, 
	based on 'most comman name' which in most cases will be company name
	  
	In order to reduce comparisons, each product will 
	be catagoried on the bases of 'most comman word'.
	Most likly it will be the name of company.
	
	Logic : make a counted list of all words in product names of master data, 
	and for each product name word which is found the most in the list will 
	be attached to product.
	
	example:
	Master data: Nokia c2 10, Nokia 1100, Karbonn K111, Karbonn K336
	list generated (key = word, value = count): {'Nokia' : 2, 'Karbonn' : 2, 'c2' : 1, '10' : 1, '1100' : 1, }
	'''
	def get_most_comman_word(self):
		self.most_comman_names = {}
		dictonary = {}
		for key in self.master_data:
			name_arr = self.master_data[key].split(' ')
			for val in name_arr:
				dictonary[val] = dictonary.get(val, 0) + 1
		for key in self.master_data:
			name_arr = self.master_data[key].split(' ')
			dict_count_of_val = [dictonary[val] for val in name_arr]
			index_key = name_arr[dict_count_of_val.index(max(dict_count_of_val))]
			if not self.most_comman_names.get(index_key, None):
				self.most_comman_names[index_key] = []
			self.most_comman_names[index_key].append(key)
				
	def find_matching_id(self, list_of_master_ids, crawled_product_name, words_match_percentage):
		for id in list_of_master_ids:
			total_words_matching_percentage = 0
			master_name = self._filter_name(self.master_data[id])
			master_name_arr = master_name.split(' ')
			crawled_product_name_arr = self._filter_name(crawled_product_name).split(' ')
#			print master_name_arr
			for mn_val in master_name_arr:
#				print mn_val
#				print crawled_product_name_arr
#				print [self.check_string_matching(mn_val, cn_val, 20) for cn_val in crawled_product_name_arr]
				if sum([self.check_string_matching(mn_val, cn_val, CONFFIG['MAX_WORD_MATCHING_ERROR'], CONFFIG['MAX_ALPHANUMBER_WORD_MATCHING_ERROR']) for cn_val in crawled_product_name_arr]) != 0:
					total_words_matching_percentage += float( 100 / len(crawled_product_name_arr))
			if int(total_words_matching_percentage) >= words_match_percentage:
#				print total_words_matching_percentage
				return id
		return None
					
	def check_string_matching(self, s1, s2, allowed_word_error_per = 0, allowed_alphanumeric_word_error_per = 0):
		distance, not_matching_characters = self.get_distance_bw_strings(s1, s2)
		error_per = float((distance * 100) / max(len(s1), len(s2)))
		
		##### Phonetic matching #####
		for char in not_matching_characters:
			if PHONETICS.get(char, None) or PHONETICS.get(not_matching_characters[char], None):
				distance -= 1
				distance += PHONETICS_DISTANCE
				
		##### condition to check alphanumeric words #####
		if re.search('\d', s1) or re.search('\d', s2):
			return float(error_per) <= float(allowed_alphanumeric_word_error_per) 
		
		return float(error_per) <= float(allowed_word_error_per)
		

		

	'''
	Returns distance between two strings and characters not matching
	
	example: 
	Nokia, Nakia -> 1, {'o' : 'a'}
	
	Reference : Levenshtein-Distance
	'''
	def get_distance_bw_strings(self, s1, s2):
		if len(s1) < len(s2):
			return self.get_distance_bw_strings(s2, s1)
		if not s1:
			return (len(s2), {})
		not_matching_characters = {}
		
		previous_row = xrange(len(s2) + 1)
		for i, c1 in enumerate(s1):
			current_row = [i + 1]
			if len(s1) == len(s2) and s1[i] != s2[i]:
				not_matching_characters[c1] = s2[i]
			for j, c2 in enumerate(s2):
				insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
				deletions = current_row[j] + 1	   # than s2
				substitutions = previous_row[j] + (c1 != c2)
				current_row.append(min(insertions, deletions, substitutions))
				
#				print insertions, deletions, substitutions
#			print str(previous_row)
			previous_row = current_row
#			print str(previous_row), "-----"
		return (previous_row[-1], not_matching_characters)
	
	
	
	def main_product_name_match(self):
		tmp = 0
		for product_name in self.crawled_data:
#			print 'product_name', product_name
			matching_id = None
			
			###### 1st pass using product codes ######
			code = self.get_product_name_code(product_name[0])
			if self.indexed_product_code.get(code, None):
#				print 'code ->' + code
#				print self.indexed_product_code[code]
				matching_id = self.find_matching_id(self.indexed_product_code[code], product_name[0], CONFFIG['MIN_MATCH_IN_PRODUCT_CODE_MODE'])
				if matching_id:
					self.output_solution.append([product_name[0], product_name[1], self.master_data[matching_id], matching_id, 'Match', 'Code B-Tree Match'])
					tmp += 1
#					print self.output_solution[-1]
					continue
			
			###### 2nd pass using B-Tree (most comman name) ######
			product_name_arr = product_name[0].split(' ')
			leaf_count_arr = [self.most_comman_names.get(val, 0) for val in product_name_arr]
			max_leaf = max(leaf_count_arr)
			node = product_name_arr[leaf_count_arr.index(max_leaf)]
			if max_leaf > 0 and self.most_comman_names.get(node, None):
#				print 'node ->' + node
#				print self.most_comman_names[node]
#				print [self.master_data[id] for id in self.most_comman_names[node]]
				matching_id = self.find_matching_id(self.most_comman_names[node], product_name[0], CONFFIG['MIN_MATCH_IN_NORMAL_MODE'])
				if matching_id:
					self.output_solution.append([product_name[0], product_name[1], self.master_data[matching_id], matching_id, 'Match', 'Comman Name B-Tree Match'])
					tmp += 1
#					print self.output_solution[-1]
					continue
				
#			###### 3rd pass in all the data ######
#			matching_id = self.find_matching_id(self.master_data.keys(), product_name[0], CONFFIG['MIN_MATCH_IN_NORMAL_MODE'])
#			if matching_id:
#				self.output_solution.append([product_name[0], product_name[1], self.master_data[matching_id], matching_id, 'Match', 'All Data'])
#				tmp += 1
#				print self.output_solution[-1]
#				continue
			if not matching_id:
				self.output_solution.append([product_name[0], product_name[1], None, None, 'No Match'])
#			print self.output_solution[-1]
		print "total code match >>" + str(tmp)
		print "total crawled data >>" + str(len(self.crawled_data))
			





if __name__ == '__main__':
	nmp = ProductNameMatching()
	nmp.main_product_name_match()
	output_writer = csv.writer(open('output.csv', 'wb'), delimiter=',')
	for row in nmp.output_solution:
		output_writer.writerow(row)
	
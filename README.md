# Name matching algorithm for phone names.

## Problem Statement

### Background and input dataset 
Every day, crawling agents scout the online market place to gather product and price data for various products/commodities. Once crawled, this data is cleansed and matched against a master database to check for uniqueness (if a given source product is already in the product master or not)  

Along with this problem statement you will also be given 3 datasets, where 
master_data.py represents Master Data for Mobiles, you will find a dictionary with Product IDs as key and Mobile Phone names as values
crawler_data represents an list of the Names and URLs of Mobiles from Infibeam.com, few examples of name crawled in a form of tuples

### What needs to be done
Task is to build a matching algorithm so that all future data sources can be matched using this matching algorithm. The expected efficiency of the algorithm is above 95%

In case the product from crawled_data is not found in the master_data, then store this also in the output.csv file, but this time mark it is as "No Match"


### Scaling Issues
* Iterations increase as the Mater Data base grows. Need to limit the number of comparisions
* Comparison should be fast, as heavier algo will make it imposible to compare in case of large data.

## Solution

### Approch to solve
* Appling a fuzzy logic based on type matching
* Phonetic matching
* Pre-processing Master Data in order to reduce number of comparisons, 
	as in case of very large crawled data processes of matching each entry in Master Data will be very heavy.
* As in this case it will be mostly product name matching, thus applying following logics in order to optimise
	* As most name contain product codes, thus search on the bases of product code (ex. for 'Nokia C2 10' code will be c210)
	* Master Data could be converted into a B-Tree
		for example: Nokia -> c2, c3 -> (10, 11), (20, 21)
		Due to time constraints only constructing a order 1 B-tree, 
		based on 'most comman name' which in most cases will be company name

### Solution
* preprocessing of master data
	* create a indexed B-Tree of order 1 for product code
	* create a indexed B-Tree of order 1 for company names
* start matching crawled data
	* 1st pass from product codes
	* 2nd pass from company names
	* 3rd pass from all the data
* write output to csv


*Note:- We can also use this algorithm for other product name matching.*
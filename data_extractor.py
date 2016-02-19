"""	
A data extraction tool.

Designed to work with fetching data from a Web Coverage Service.  It will then extract either :

simple polygon extraction (simple) - extracts data from within a regular polygon per time slice, runs summary stats (min,max,mean,median,std) and returns json object per time step

irregular polygon extraction (irregular) - same as simple polygon but takes a complex user defined polygon

transect latitude extraction (trans-lat) - extracts data from a POLYLINE, then returns stats moving along the latitude axis

transect longitude extraction (trans-long) - extracts data from a POLYLINE, then returns stats moving along the latitude axis

transect time extraction (trans-time) - extracts data from a POLYLINE, then returns stats moving along a time axis

example wcs url : http://rsg.pml.ac.uk/thredds/wcs/CCI_ALL-v2.0-MONTHLY?service=WCS&version=1.0.0&request=GetCapabilities

example calling : python data_extractor.py -t basic -g "POLYGON((-28.125 43.418,-19.512 43.77,-18.809 34.453,-27.07 34.629,-28.125 43.418))" -url http://rsg.pml.ac.uk/thredds/wcs/CCI_ALL-v2.0-MONTHLY -var chlor_a -time 2010-01-01/2011-01-01

"""

import argparse
from extractors import BasicExtractor, IrregularExtractor, TransectExtractor, SingleExtractor
from extraction_utils import Debug, get_transect_bounds, get_transect_times
from analysis_types import BasicStats, TransectStats
from shapely import wkt

def main():

	usage = "a usage string" 

	parser = argparse.ArgumentParser(description=usage)
	parser.add_argument("-t", "--type", action="store", dest="extract_type", help="Extraction type to perform", required=True, choices=["single","basic","irregular","trans-lat","trans-long","trans-time"])
	parser.add_argument("-o", "--output", action="store", dest="output", help="Choose the output type (only json is currently available)", required=False, choices=["json"], default="json")
	parser.add_argument("-url", "--wcs_url", action="store", dest="wcs_url", help="The URL of the Web Coverage Service to get data from", required=True)
	parser.add_argument("-var", "--variable", action="store", dest="wcs_variable", help="The variable/coverage to request from WCS", required=True)
	parser.add_argument("-v", "--debug", action="store_true", dest="debug", help="a debug flag - if passed there will be a tonne of log output and all interim files will be saved", required=False)
	parser.add_argument("-d", "--depth", action="store", dest="depth", help="an optional depth parameter for sending to WCS", required=False, default=0)
	parser.add_argument("-g", "--geom", action="store", dest="geom", help="A string representation of teh polygon to extract", required=False)#, default="POLYGON((-28.125 43.418,-19.512 43.77,-18.809 34.453,-27.07 34.629,-28.125 43.418))")
	parser.add_argument("-b", "--bbox", action="store", dest="bbox", help="A string representation of teh polygon to extract", required=False)
	parser.add_argument("-time", action="store", dest="time", help="A time string for in the format startdate/enddate or a single date", required=True)
	parser.add_argument("-mask", action="store", dest="mask", help="a polygon representing teh irregular area", required=False)
	parser.add_argument("-csv", action="store", dest="csv", help="a csv file with lat,lon,date for use in transect extraction", required=False)
	args = parser.parse_args()

	#print args.debug
	debug = Debug(args.debug)
	debug.log("a message to test debugging")

	if(args.geom):
		#print "geom found - generating bbox"
		bbox = wkt.loads(args.geom).bounds
		#print bbox
	if(args.bbox):
		bbox = [args.bbox]



	if (args.extract_type == "basic"):
		extractor = BasicExtractor(args.wcs_url, [args.time], extract_area=bbox, extract_variable=args.wcs_variable)
		filename = extractor.getData()
		stats = BasicStats(filename, args.wcs_variable)
		output_data = stats.process()
	elif (args.extract_type == "irregular"):
		extractor = IrregularExtractor(args.wcs_url, [args.time], extract_area=bbox, extract_variable=args.wcs_variable, masking_polygon=args.geom)
		filename = extractor.getData()
		stats = filename
	elif (args.extract_type == "trans-lat"):
		extractor = TransectExtractor(args.wcs_url, [args.time], "latitude",  extract_area=bbox, extract_variable=args.wcs_variable)
		filename = extractor.getData()
		#print filename
	elif (args.extract_type == "trans-long"):
		extractor = TransectExtractor(args.wcs_url, ["2011-01-01", "2012-01-01"], "longitude", extract_area=bbox, extract_variable=args.wcs_variable)
		filename = extractor.getData()
	elif (args.extract_type == "trans-time"):
		# we will accept csv here so we need to grab teh lat lons and dates for use within teh extractor below
		#csv = open(args.csv, "r").read()
		bbox = get_transect_bounds(args.csv)
		time = get_transect_times(args.csv)
		extractor = TransectExtractor(args.wcs_url, [time], "time", extract_area=bbox, extract_variable=args.wcs_variable)
		filename = extractor.getData()
		stats = TransectStats(filename, args.wcs_variable, args.csv)
		output_data = stats.process()
	elif (args.extract_type == "single"):
		extractor = SingleExtractor(args.wcs_url, args.time, extract_area=bbox, extract_variable=args.wcs_variable)
		output_data = extractor.getData()
	else :
		raise ValueError('extract type not recognised! must be one of ["basic","irregular","trans-lat","trans-long","trans-time"]')

	print output_data









if __name__ == '__main__':
	main()
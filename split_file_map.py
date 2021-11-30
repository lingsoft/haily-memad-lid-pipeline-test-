# This script map the corresponding time segment to the output 

import csv
import datetime
import os
import sys


with open('segments.csv', 'r', encoding='UTF8') as f:
  csv_reader = csv.reader(f, delimiter=',')
  for row in csv_reader:
    fname, start, end = row[0],int(float(row[1])), int(float(row[2]))
    new_fname = fname.split('.')[0] + '_' + str(datetime.timedelta(seconds=start)) + \
                '_' + str(datetime.timedelta(seconds=end)) + '.wav'
    #print('new f_name', new_fname)
    outdir = os.environ['OUTDIR']
    os.rename(outdir + '/'+ fname, outdir + '/'+ new_fname)



    
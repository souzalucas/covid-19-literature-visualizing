#python3 csv_to_bib.py sample_metadata.csv

import os
import sys
import csv
import rispy
import time
import fix_bibtex_errors

start_time = time.time()

os.system('mkdir dados')
os.system('mkdir dados/split')
os.system('mkdir dados/split/ris')
os.system('mkdir dados/split/bib')

N_MAX_AUTHORS_PER_PAPER = 100

bib_file_names = []

csvfile = open(sys.argv[1], newline='')

reader = csv.DictReader(csvfile)

j = 0

while (j < 10):

  ris_file_name = "dados/split/ris/part_" + str(j) + ".ris"

  with open(ris_file_name, 'a') as bibliography_file:

    i = 0

    for row in reader:

      list_authors = row['authors'].split("; ")
      if (len(list_authors) > N_MAX_AUTHORS_PER_PAPER): continue

      publication_year = row['publish_time'].split("-")[0]

      entries = [{
        'type_of_reference': 'JOUR',
        'title': row['title'],
        'first_authors': list_authors,
        'abstract': row['abstract'],
        'publication_year': publication_year,
        'doi': row['doi'],
        'journal_name': row['journal'],
        'url': row['url']
      }]

      rispy.dump(entries, bibliography_file)

      i += 1

      if (i >= 105666): break

    print(ris_file_name + " OK!!")

    bib_file_names.append("dados/split/bib/part_" + str(j) + ".bib")

    os.system('ris2xml ' + ris_file_name + ' | xml2bib > ' + bib_file_names[j])

    print(bib_file_names[j] + " OK!!")

    j += 1

file_names = ""
for file_name in bib_file_names:

  file_names += file_name+" "

os.system('cat ' + file_names + '> dados/split/bib/full.bib')

print("dados/split/bib/full.bib OK!!")

fix_bibtex_errors_1.main("dados/split/bib/full.bib")

print("--- %s min ---" % ((time.time() - start_time)/60))

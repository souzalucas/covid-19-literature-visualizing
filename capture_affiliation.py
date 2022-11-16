# Gera um arquivo csv para carregar no datawrapper (mapa coroplético)
# No arquivo de saída, a partir da linha com "------,-------" são os países que não puderam ser identificados
# Usar no datawrapper apenas as linhas anteriores a essa

# python3 capture_affiliation.py sample_metadata.csv normalized_countries.csv out.csv

import sys
import csv
import json
from jsonpath_ng import parse
import time

PATH_CORD_19 = '/media/lucas/3D1CCA42663CADBE/cord-19_2022-06-02/2022-06-02/'

EXPRESSION_SEARCH_AFFILIATION = 'metadata.authors[*].affiliation.location.country'

normalized_countries = {}

count_countries_recognized = {}

count_countries_unrecognized = {}

countries_list = []

papers_with_identified_country = 0
papers_with_not_identified_country = 0

common_names = {
  "usa":           "United States of America", 
  "u s a":         "United States of America", 
  "u.s.a":         "United States of America", 
  "united states": "United States of America", 
  "u. s. a":       "United States of America", 
  "uk":            "United Kingdom", 
  "u.k":           "United Kingdom", 
  "u k":           "United Kingdom",
  "brasil":        "Brazil",
  "iran":          "Islamic Republic of Iran"
}

def create_dictionary():

  global countries_list

  with open(sys.argv[2], newline='') as file:

    reader = csv.reader(file)

    countries_list = next(reader)

    file.seek(0)

    zipped = zip(*reader)

    for column in zipped:

      for name in column[1:]:

        if (name != ''):

          normalized_countries[name] = column[0]


def open_csv_metadata():

  with open(sys.argv[1], newline='') as csvfile:

    reader = csv.DictReader(csvfile)

    return list(reader)


def analize_json_file(path):

  if path != '':

    with open(PATH_CORD_19 + path) as myfile:
        
      data = json.load(myfile)

      jsonpath_expression = parse(EXPRESSION_SEARCH_AFFILIATION)

      return jsonpath_expression.find(data)


def add_country_in_dict(country, c_in_this_paper, dict):

  if country not in c_in_this_paper:

    c_in_this_paper.append(country)

    dict[country] = 1 if country not in dict else dict[country]+1


def try_1(country, countries_in_this_paper):

  if country in normalized_countries:

    add_country_in_dict(normalized_countries[country], countries_in_this_paper, count_countries_recognized)

    return True

  else: return False


def try_2(country, countries_in_this_paper):

  found = False
  
  for canonical_name in countries_list:
    
    if(canonical_name.lower() in country): 
      
      add_country_in_dict(canonical_name, countries_in_this_paper, count_countries_recognized)
      
      found = True

  return found


def try_3(country, countries_in_this_paper):

  found = False

  for key, value in normalized_countries.items():
    
    if(key in country): 
      
      add_country_in_dict(value, countries_in_this_paper, count_countries_recognized)

      found = True

  return found


def recognize_country(country, countries_in_this_paper):

  country = country.value.strip().lower()

  recognized = try_1(country, countries_in_this_paper)

  if not recognized:

    country_split = country.split(",")

    for country in country_split:

      country = country.strip().lower()

      recognized = try_1(country, countries_in_this_paper)

      if not recognized:

        recognized = try_2(country, countries_in_this_paper)

        if not recognized:

          recognized = try_3(country, countries_in_this_paper)

          add_country_in_dict(country, countries_in_this_paper, count_countries_unrecognized) if not recognized else ""


def write_in_csv():

  with open(sys.argv[3], 'w', encoding='UTF8') as file_countries:

    header = ['Country', 'Value']
    
    writer = csv.writer(file_countries)

    writer.writerow(header)

    for key, value in count_countries_recognized.items():

      writer.writerow([key, value])

    writer.writerow(['----------------------', '----------------------'])

    for key, value in count_countries_unrecognized.items():

      writer.writerow([key, value])

  with open(sys.argv[3][:-4]+"_log.txt", 'w') as file_countries_log:

    file_countries_log.write("Papers with identified country: " + str(papers_with_identified_country) + "\n")
    file_countries_log.write("Papers without identified country: " + str(papers_with_not_identified_country))


def main():

  global papers_with_identified_country
  global papers_with_not_identified_country

  start = time.perf_counter()

  create_dictionary()

  reader_csv_metadata = open_csv_metadata()

  # para cada artigo de metadata.csv
  for row in reader_csv_metadata:

    countries_in_this_paper = []

    paths_json_files = row['pdf_json_files'].split("; ")

    # para cada arquivo json deste artigo
    for path in paths_json_files:

      found_countries = analize_json_file(path)

      if found_countries != None:
        
        # para cada país encontrado neste arquivo
        for country in found_countries:

          recognize_country(country, countries_in_this_paper)

    if (len(countries_in_this_paper) > 0): papers_with_identified_country += 1
    else: papers_with_not_identified_country += 1

  end = time.perf_counter()
  runtime = (end-start)/60
  print(runtime)
  
  # escrever em um arquivo csv
  write_in_csv()


main()

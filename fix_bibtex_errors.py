import sys
import re

def main(path_file_in):

  authors = ''
  riding = 0

  with open(path_file_in, 'r') as file_in, open(path_file_in + "_fixed.bib", 'w') as file_out:

    for line in file_in:

      if line[0:6] == 'author' and line[-2] != ',':

        authors = line[0:-1]

        riding = 1

      elif line[0:3] == 'and':

        authors += ' ' + line[:-1]

      else:

        if riding == 1:

          file_out.write(re.sub("@", "\@", authors)+'\n')

          riding = 0

        if "@Article" in line:

          file_out.write(line)

        else:

          file_out.write(re.sub("@", "\@", line))
        
  print(path_file_in + "_fixed.bib OK!!")


#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import multiprocessing
import os
import sys
import time

if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

for path in [os.getcwd(),"software/Util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource
from sdoterm import *
from schemaexamples import SchemaExamples


def termFileName(termid):
  """Generate filename for term page.

  Parameters:
    termid (str): term identifier.
  Returns:
    File path the term page should be generated at.
  """
  path_components = [OUTPUTDIR, "terms"]
  if re.match('^[a-z].*',termid):
    path_components.append('properties')
  elif re.match('^[0-9A-Z].*',termid):
    path_components.append('types')
  else:
    raise ValueError("Invalid terminid: '" + termid +"'")
  path_components.append(termid[0])
  directory = os.path.join(*path_components)
  checkFilePath(directory)
  filename = termid + '.html'
  return os.path.join(directory, filename)


# This template will be used ~2800 times, so we reuse it.
TEMPLATE = jenv.get_template("terms/TermPage.j2")

def termtemplateRender(term, examples, json):
  """Render the term with examples and associated JSON.

  Parameters:
    term (sdoterm.SdoTerm): term to generate the page for
    examples (schemaexamples.Example): collection of examples for the term.
  Returns:
    string with the generate web-page.
  """

  print(">>> %s " % hasOpt("goto"))
  extra_vars = {
      'title': term.label,
      'menu_sel': "Schemas",
      'home_page': "False",
      'BUILDOPTS': BUILDOPTS,
      'docsdir': TERMDOCSDIR,
      'term': term,
      'jsonldPayload': json,
      'examples': examples
  }
  return templateRender(template_path=None, extra_vars=extra_vars, template_instance=TEMPLATE)


def RenderAndWriteSingleTerm(term_key):
  """Renders a single term and write the result into a file.

  Parameters:
    term_key (str): key for the term.
  Returns:
    elapsed time for the generation (seconds).
  """
  tic = time.perf_counter()
  term = SdoTermSource.getTerm(term_key, expanded=True)
  if not term:
    print("No such term: %s\n" % term_key)
    return 0
  if term.termType == SdoTerm.REFERENCE: #Don't create pages for reference types
    return 0
  examples = SchemaExamples.examplesForTerm(term.id)
  json = SdoTermSource.getTermAsRdfString(term.id, "json-ld", full=True)
  pageout = termtemplateRender(term, examples, json)
  with open(termFileName(term.id), 'w', encoding='utf8') as outfile:
    outfile.write(pageout)
  elapsed = time.perf_counter() - tic
  print("Term '%s' generated in %0.4f seconds" % (term_key, elapsed))
  return elapsed


def buildTerms(terms):
  """Build the rendered version for a collection of terms."""
  if any(filter(lambda term: term in ("ALL","All","all"), terms)):
    terms = SdoTermSource.getAllTerms(supressSourceLinks=True)

  if terms:
    print("\nBuilding %d term pages...\n" % len(terms))

  total_elapsed = 0
  for term_key in terms:
    total_elapsed += RenderAndWriteSingleTerm(term_key)

  print("%s terms generated in %0.4f seconds" % (len(terms), total_elapsed))



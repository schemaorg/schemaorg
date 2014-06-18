#!/usr/bin/env python
#

import webapp2
import re
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import xml.etree.ElementTree as ET
import logging

headers = '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>%s - schema.org</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css"
          href="/docs/schemaorg.css" />

    <link href="/docs/prettify.css" type="text/css"
          rel="stylesheet" />
    <script type="text/javascript" src="/docs/prettify.js">
    </script>
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>

<script type="text/javascript">
      $(document).ready(function(){
        prettyPrint();
        setTimeout(function(){

  $(".atn:contains(itemscope), .atn:contains(itemtype), .atn:contains(itemprop), .atn:contains(itemid), .atn:contains(time), .atn:contains(datetime), .atn:contains(datetime), .tag:contains(time) ").addClass(\'new\');
  $('.new + .pun + .atv\').addClass(\'curl\');

        }, 500);
        setTimeout(function(){

  $(".atn:contains(property), .atn:contains(typeof) ").addClass(\'new\');
  $('.new + .pun + .atv\').addClass(\'curl\');

        }, 500);
        setTimeout(function() {
          $('.ds-selector-tabs .selectors a').click(function() {
            var $this = $(this);
            var $p = $this.parents('.ds-selector-tabs');
            $('.selected', $p).removeClass('selected');
            $this.addClass('selected');
            $('pre.' + $this.data('selects'), $p).addClass('selected');
          });
        }, 0);
      });
</script>

<style>

  .pln    { color: #444;    } /* plain text                 */
  .tag    { color: #515484; } /* div, span, a, etc          */
  .atn,
  .atv    { color: #314B17; } /* href, datetime             */
  .new    { color: #660003; } /* itemscope, itemtype, etc,. */
  .curl   { color: #080;    } /* new url                    */
  
  table.definition-table { 
    border-spacing: 3px;
    border-collapse: separate;
  }

</style>

</head>
<body>
    <div id="container">
        <div id="intro">
            <div id="pageHeader">
              <div class="wrapper">
                <h1>schema.org</h1>

<div id="cse-search-form" style="width: 400px;"></div>

<script type="text/javascript" src="//www.google.com/jsapi"></script>
<script type="text/javascript">
  google.load(\'search\', \'1\', {language : \'en\', style : google.loader.themes.ESPRESSO});
  google.setOnLoadCallback(function() {
    var customSearchControl = new google.search.CustomSearchControl(\'013516846811604855281:nj5laplixaa\');
    customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
    var options = new google.search.DrawOptions();
    options.enableSearchboxOnly("/docs/search_results.html", null, false, \'#\');
    customSearchControl.draw(\'cse-search-form\', options);
  }, true);
</script>


              </div>
            </div>
        </div>
    </div>

            <div id="selectionbar">
               <div class="wrapper">
                <ul>
                    <li >
                      <a href="docs/documents.html">Documentation</a></li>
                    <li class="activelink">
                      <a href="docs/schemas.html">Schemas</a></li>
                    <li >
                      <a href=".">Home</a></li>
                </ul>
                </div>

            </div>
        <div style="padding: 14px; float: right;" id="languagebox"></div>



  <div id="mainContent" vocab="http://schema.org/" typeof="%s" resource="http://schema.org/%s">
  %s

'''

def OutputSchemaorgHeaders(webapp, entry='', is_class=False, ext_mappings=''):
    """
    Generates the headers for class and property pages

    * entry = name of the class or property
    """

    rdfs_type = 'rdfs:Property'
    if is_class:
        rdfs_type = 'rdfs:Class'
    out = headers % (str(entry), rdfs_type, str(entry), ext_mappings)
    webapp.response.write(out)

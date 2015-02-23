<?php
/**
 * Genereates a CSV file in with all properties, grouped by its domain-classes.
 * @see https://github.com/schemaorg/schemaorg/issues/355
 * @usege 1) php generateCSV.php > generatedDATE.csv;  
 *        2) point LivreOffice or Excell to the csv file;
 *        3) set importing form to "olny tab" and empty delimitator. 
 *        4) save and import at Google-docs.
 */

$dom = new DOMDocument('1.0','UTF-8');
$dom->load('../../../data/schema.rdfa');
$xp = new DOMXpath($dom);
$allProps = array();
$INCs = 'http://schema.org/domainIncludes';

print "WikidataID\tType\tLabel\tComment";

// SCAN AND PRINT:
foreach (iterator_to_array($xp->query("//div[@typeof='rdfs:Class']")) as $i) {
	//$class=$i->nodeValue;
	$class = getSpan($i,'rdfs:label');
	$descr = getSpan($i,'rdfs:comment');
	print "\nQ?\tClass   \t$class\t$descr";
	$q = "//div[@typeof='rdf:Property' and ./span/a[@property='$INCs' and @href='http://schema.org/$class']]";
	foreach (iterator_to_array($xp->query($q)) as $j) if ( ($p=getSpan($j)) && !isset($allProps[$p]) ) {
		$descr = getSpan($j,'rdfs:comment');
		print "\nQ?\t- Property\t$p\t$descr";
		$allProps[$p]=1;
	}
}

// VALIDATION:
$N = $xp->query("//div[@typeof='rdf:Property']")->length;
if ($N!=count(array_keys($allProps))) {
	foreach (iterator_to_array($xp->query("//div[@typeof='rdf:Property']/span[@property='rdfs:label']")) as $i)
		if ( ($p=$i->nodeValue) && !isset($allProps[$p]) ) 
			print "\n * ERROR: property '$p' without Class.";
	// see detected bugs at https://github.com/schemaorg/schemaorg/issues/355
}

print "\n";

// // // LIB

function getSpan($node,$prop='rdfs:label') {
	global $xp;
	$s = $xp->evaluate("string(span[@property='$prop'])",$node);
	$s = str_replace("\n"," ",html_entity_decode($s,ENT_HTML5));
	if (mb_strlen($s,'UTF-8')>250)
		return mb_substr($s, 0,250).' (...)';
	else 
		return $s;
}


?>

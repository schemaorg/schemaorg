<?php
/**
 * Updates schema.rdfa with the CSV file, and vice-versa.
 * USE after check bellow the main configs (!).
 * USE after update or get original schema.rdfa:
 *   php updatesRDFbyCSV.php > spreadsheets/updated2015-02-23.csv
 * USE after update (edit) the spreadsheet and export it back to here:
 *   php updatesRDFbyCSV.php -u > schema.rdfa.htm
 *
 * @see https://github.com/schemaorg/schemaorg/issues/355
 * @see https://github.com/schemaorg/schemaorg/issues/359
 * @see https://github.com/schemaorg/schemaorg/issues/360 
 */

// MAIN CONFIGS
$schemaFile = '../../../data/schema.rdfa';  // original
//or $schemaFile = 'schema.rdfa.htm';			// rewrited
$csvFile = 'spreadsheets/updated2015-02-23.csv';
$cmd     = isset($argv[1])? $argv[1]: '';


// SECONDARY CONFIGS
$csvFile_sep = "\t";
$csvFile_lineMaxLen = 900;
$nmax = 0;  // non-zero for debug first lines
$LSP = ' '; // last space in a <closed/> tag.
$stderr = 'php://stderr';
$isTerminal = true;



////////////////////////////////////////
////////////////////////////////////////
if ($cmd=='-u') {// UPDATE COMMAND  ////

	// DOM INITIALIZE
	$dom = new DOMDocument('1.0','UTF-8');
	$dom->substituteEntities = false; // no effect!
	//$dom->load($schemaFile);
	$dom->loadXML( xml_entity_decode(file_get_contents($schemaFile),$mode='10') );

	$dom->encoding = 'UTF-8'; // for loaded
	$dom->substituteEntities = false; // no effect!

	// CSV INITIALIZE
	$h = fopen($csvFile,'r');

	// SCAN AND UPDATE LOOP:
	$n=$n2=0;
	$xp = new DOMXpath($dom);
	while( !feof($h) && (!$nmax || $n<$nmax) ) {
		$n++;
		$r = fgetcsv($h,$csvFile_lineMaxLen,$csvFile_sep);
		if ( $n>1  && $r[2]) { // line cond
			$r = array_map('trim', $r);
			$isClass = (strtolower($r[2])=='class'); // vai mudar para detecção de primeira maiuscula!
			$type    = $isClass? 'rdfs:Class': 'rdf:Property';
			$wID     = preg_match('/Q\d+/',$r[0])? $r[0]: '';
			$isSub   = $r[1]? true: false;
			$name    = $r[3];
			if ($wID){
				$q = "//div[@typeof='$type' and @resource='http://schema.org/$name']";
				$node = $xp->query($q)->item(0); // one occurence hypothesis
				$label = $xp->evaluate("string(span[@property='rdfs:label'])",$node);
				/* Debug link tags:
				foreach (iterator_to_array($xp->query("link",$node)) as $lk) {
					$lkp = $lk->getAttribute('property');
					$lkh = $lk->getAttribute('href');
					print "\n\t -- $lkp=$lkh";
	// normalize to SPAN, wait @elf-pavlik 
				}
				*/
				$OWL = $isClass? 
					($isSub? 'rdfs:subClassOf':    'owl:equivalentClass'): 
					($isSub? 'rdfs:subPropertyOf': 'owl:equivalentProperty');
				$newHref = "https://www.wikidata.org/wiki/$wID";	
				$linkCt = $xp->query("link[contains(translate(@href,'WIKDATORG','wikdatorg'),'wikidata.org')]",$node);
				if ($linkCt->length) { 	// // CHANGE link tag:  // //
					$lk = $linkCt->item(0);
					$oldProp = $lk->getAttribute('property');
					$oldID   = $lk->getAttribute('href');
					if ($oldProp!=$OWL || $oldID!=$newHref)
						$msg("NOTICE: was $linkProp($oldID), now is $OWL($wID)");
				} else			
					$lk = $dom->createElement('link');
				$lk->setAttribute('property',$OWL);
				$lk->setAttribute('href',$newHref);
				if (!$linkCt->length)	// ADD a link tag.
					$node->appendChild($lk);
				// debug msg( $dom->saveXML($node) );	
				$isSub = $isSub? '<': '=';
				$isClass = $isClass? '': ' ';
				msg("line $n.\t$isClass $name $isSub $wID");
			}
			$n2++;
		}
	} // loop file
	fclose($h);
	msg("\n"); 
	$s = xml_entity_decode( $dom->saveXML() );  // C14N or saveXML
	$s = preg_replace('#\s*<((?:link|hr|br|meta)[^>]*)\s*/>#uis', "\n      <\$1$LSP/>",$s); // tidy and LSP
	print $s;
}	//////////////// END UPDATE COMMAND
else
{
	////////////////////////////////////////
	////////////////////////////////////////
	            // CSV FILE GENERATOR  ////

	// DOM INITIALIZE
	$dom = new DOMDocument('1.0','UTF-8');
	$dom->load( $schemaFile );
	$dom->encoding = 'UTF-8'; // after load
	$xp = new DOMXpath($dom);

	// SCAN AND UPDATE LOOP:
	$n=$n2=0;


	$allProps = array();
	$supBy = array();
	$INCs = 'http://schema.org/domainIncludes';
	$WQ = ''; // 'Q?';
	print "WikidataID\tisSub\tLabel\tComment";
	// SCAN AND PRINT:
	foreach (iterator_to_array($xp->query("//div[@typeof='rdfs:Class']")) as $i) {
		//$class=$i->nodeValue;
		$class = getSpan($i,'rdfs:label');
		$descr = getSpan($i,'rdfs:comment');
		if ( getSpan($i,'supBy') )
			$supBy[] = $class;
		else
			printLine($i,$class,$descr);
		$q = "//div[@typeof='rdf:Property' and ./span/a[@property='$INCs' and @href='http://schema.org/$class']]";
		foreach (iterator_to_array($xp->query($q)) as $j) if ( ($p=getSpan($j)) && !isset($allProps[$p]) ) {
			$descr = getSpan($j,'rdfs:comment');
			if ( getSpan($j,'supBy') )
				$supBy[] = $p;
			else
				printLine($j," $p",$descr);
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

	if (count($supBy)) {
		$nSup=1;
		print "\n---- items supersededBy ----";
		foreach ($supBy as $label)
			echo "\n\t", $nSup++, " $label";
	}
	print "\n";

}


// // // LIB

function getSpan($node,$prop='rdfs:label') {
	global $xp;
	if ($prop=='supBy')
		return $xp->evaluate("boolean(span[@property='http://schema.org/supersededBy']/@property)",$node);	
	$s = $xp->evaluate("string(span[@property='$prop'])",$node);
	$s = str_replace("\n"," ",html_entity_decode($s,ENT_HTML5));
	if (mb_strlen($s,'UTF-8')>250)
		return mb_substr($s, 0,250).' (...)';
	else 
		return $s;
}

function xml_entity_decode($s,$mode='11') {
	// mode="IF" flags; I=initial process; F=Final process. 
	//  1X =  initial. 
	//  X1 =  final. Danger when "01".
	$XENTITIES = array('&amp;','&gt;','&lt;',   '&quot;', '&#39;');
	$XSAFENTITIES = array('#_xX_amp#;','#_xX_gt#;','#_xX_lt#;', '#_xX_quot#;','#_xX_qt39#;');
	$mode = str_split($mode);	
	if ($mode[0])
		$s = str_replace($XENTITIES,$XSAFENTITIES,$s);
	if ($mode[1]) {
		$s = html_entity_decode($s, ENT_HTML5|ENT_NOQUOTES, 'UTF-8'); // PHP 5.3+
		$s = str_replace($XSAFENTITIES,$XENTITIES,$s);
	}
	return $s;
}  

///////////////////


function msg($msg) {
	global $stderr;
	global $isTerminal;
	$msg = $isTerminal? "\n\t --$msg": ("\n<br/> --- ".htmlentities($msg));
	file_put_contents($stderr,$msg);	
}


function printLine($node,$class,$descr){
	global $xp;
	global $WQ;
	$QLINK = "link[contains(translate(@href,'WIKDATORG','wikdatorg'),'wikidata.org')]";
	$oldSub = '';
	$oldID = $WQ;
	$linkCt = $xp->query($QLINK,$node);
	if ($linkCt->length) {
		$lk = $linkCt->item(0);
		if ( preg_match('#[^/]/(.\d+)$#',$lk->getAttribute('href'),$m) ) 
			$oldID   = $m[1];
		$oldSub = preg_match('/sub/i',$lk->getAttribute('property'));
	}
	$oldSub = $oldSub? 'X': '';
	print "\n$oldID\t$oldSub\t$class\t$descr";
}

?>

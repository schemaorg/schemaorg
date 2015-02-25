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
$schemaFile = '../../../data/schema.rdfa';  // original (default)
// $schemaFile = 'schema.rdfa.htm';			// rewrited
$schemaFile = '../../../proposals/testing/releases/r2015-02-04-v1.93-sdoStantz.schema.rdfa.htm';

$csvFile = 'spreadsheets/updated2015-02-23b.csv';
$cmd     = isset($argv[1])? $argv[1]: '';


// SECONDARY CONFIGS
$csvFile_sep = "\t";
$csvFile_lineMaxLen = 900;
$nmax = 0;  // non-zero for debug first lines
$LSP = ' '; // last space in a <closed/> tag.
$stderr = 'php://stderr';
$isTerminal = true;
$U = 'http://schema.org'; // urlBase
$INCs = "$U/domainIncludes";



////////////////////////////////////////
////////////////////////////////////////
if ($cmd=='-c' || $cmd=='-r') {// COUNT AND REPORT COMMANDS  ////
	$dom = new DOMDocument('1.0','UTF-8');
	$dom->load($schemaFile);
	$xp = new DOMXpath($dom);

	$rep=array(  // general counting report
		'nDivs'=>array(0,'number of div tags'),
		'nDefs'=>array(0,'number of definitions by classes+properties'),
		'nClass'=>array(0,'number of rdfs-classes'),
		'nProp'=>array(0,'number of rdf-Properties'),
		'nSupBy'=>array(0,'number of schema-supersededBy'),
		'nDup'=>array(0,'number of duplicated rdfs-labels'),
		//'x'=>array(0,'number of '),
	);
	$repLks=array(  // report of links and spans
		'lktypes'=>array(array(),'number of defs with link tag'),
		'nLinks'=>array(0,'number of defs with link tag'),
		'nLinksTot'=>array(0,'total number of link tags over defs'),
		'nY'=>array(0,'number of spans'),
	);

	print "\n ---- REPORT ($schemaFile)... ----";
	$all = array();
	$supBy = array();
	foreach (iterator_to_array($xp->query("//div[@typeof='rdfs:Class' or @typeof='rdf:Property']")) as $i) {
		$rep['nDivs'][0]++;
		$isClass = ($i->getAttribute('typeof')==='rdfs:Class');
		$label = getSpan($i,'rdfs:label');
		$res   = $i->getAttribute('resource');
		$firstLetter = substr($label,0,1);
		$isPropByLabel = (strtolower($firstLetter)==$firstLetter);

		if (!$res)
			msg("ERROR-1 (no resouce) on div.");
		elseif (!$label)
			msg("ERROR-2 (no label) on $res .");
		elseif ( getSpan($i,'supBy') )
			$rep['nSupBy'][0]++;  // property="supersededBy" or "http://schema.org/supersededBy"
		else {
			if (isset($all[$label])) $all[$label]++; else $all[$label]=1; // for nDup
			if ($isClass) {
				if ($isPropByLabel)
					msg("ERROR-3 on label of class '$label'.");
				$rep['nClass'][0]++;
			} else {
				if (!$isPropByLabel)
					msg("ERROR-4 on label of property '$label'.");
				$rep['nProp'][0]++;
			} // isClass
			// check links and spans:
			$xpq_link = $xp->query("link",$i);
			$aux = $xpq_link->length;
			if ($aux) {
				$repLks['nLinks'][0]++;
				$repLks['nLinksTot'][0] += $aux;	
			}
			if ($cmd=='-r') {
				foreach (iterator_to_array($xpq_link) as $lk) {
					$lkp = $lk->getAttribute('property');
					$lkh = $lk->getAttribute('href');
					//debug print "\n\t -- $lkp=$lkh";
					if (isset($repLks['lktypes'][0][$lkp])) $repLks['lktypes'][0][$lkp]++; 
					else $repLks['lktypes'][0][$lkp]=1; // for nDup
				} // for
			} // if -r
		} // if errors

	} // for node $i
	$rep['nDefs'][0] = $rep['nClass'][0]+$rep['nProp'][0];
	foreach ($all as $k=>$v) if ($v>1) {
		$rep['nDup'][0]++;
		msg("ERROR-15 $k duplicated."); 
	}
	print "\n\t **COUNTINGS:**";
	$rep['nLinks'] = $repLks['nLinks'];
	if ($rep['nLinks'][0])
		$rep['nLinksTot'] = $repLks['nLinksTot'];	
	foreach($rep as $k=>$r) {
		print "\n\t * $r[1] ($k): **$r[0]**";
	}
	if ($cmd=='-r') {
		print "\n\t **tag link countings**";
		foreach($repLks['lktypes'][0] as $prop=>$n) {
			print "\n\t\t * links with property='$prop': **$n**";
		}
	}
	print "\n";

////////////////////////////////////////
////////////////////////////////////////
} elseif ($cmd=='-u') {// UPDATE COMMAND  ////

	// DOM INITIALIZE
	$dom = new DOMDocument('1.0','UTF-8');
	//$dom->load($schemaFile);
	$dom->loadXML( xml_entity_decode(file_get_contents($schemaFile),$mode='10') );
	$dom->encoding = 'UTF-8'; // for loaded
	$dom->substituteEntities = false; // no effect!
	$xp = new DOMXpath($dom); // back out 

	// CSV INITIALIZE
	$h = fopen($csvFile,'r');

	// SCAN AND UPDATE LOOP:
	$n=$n2=0;
	while( !feof($h) && (!$nmax || $n<$nmax) ) {
		$n++;
		$r = fgetcsv($h,$csvFile_lineMaxLen,$csvFile_sep);
		if ( $n>1  && $r[2]) { // line contains data
			$r = array_map('trim', $r);
			$name    = $r[2];

			$firstLetter = substr($name,0,1);
			$isPropByLabel = (strtolower($firstLetter)==$firstLetter);
			$isClass = (!$isPropByLabel); // ops, but ok
			$type    = $isClass? 'rdfs:Class': 'rdf:Property';
			$wID     = preg_match('/Q\d+/',$r[0])? $r[0]: '';
			$isSub   = $r[1]? true: false;
			if ($wID){
				$q = "//div[@typeof='$type' and @resource='$U/$name']";
				$node = $xp->query($q)->item(0); // one occurence hypothesis
				$label = $xp->evaluate("string(span[@property='rdfs:label'])",$node);
				/* Debug link tags:
				foreach (iterator_to_array($xp->query("link",$node)) as $lk) {
					$lkp = $lk->getAttribute('property');
					$lkh = $lk->getAttribute('href');
					print "\n\t -- $lkp=$lkh";
				}
				*/
				if ($label){

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
							msg("NOTICE: was $oldProp($oldID), now is $OWL($wID)");
					} else			
						$lk = $dom->createElement('link');
					$lk->setAttribute('property',$OWL);
					$lk->setAttribute('href',$newHref);
					if (!$linkCt->length)	// ADD a link tag.
						$node->appendChild($lk);
					$isSub = $isSub? '<': '=';
					$isClass = $isClass? '': ' ';
					msg("line $n.\t$isClass $name $isSub $wID");					

				} // if label

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
		$q = "//div[@typeof='rdf:Property' and ./span/a[@property='$INCs' and @href='$U/$class']]";
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
	global $U;
	if ($prop=='supBy')
		return $xp->evaluate("boolean(span[@property='$U/supersededBy']/@property)",$node);	
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

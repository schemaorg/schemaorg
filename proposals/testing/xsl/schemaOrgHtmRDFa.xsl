<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<!-- ============================================================== -->
<!--  MODULE:  ViewFull-HTML                                        -->
<!--  DESCR:   final schema_org_rdfa.html generator.                -->
<!--  DEPENDENCES: external non-XSLTv1 functions.                   -->
<!--  NOTE: any "sanitize" filter MUST be triggered here.           -->
<!--                                                                -->
<!--  AUTHOR:  Schema.org        LICENCE: CC BY-SA                  -->
<!--  VERSION: 1.0               DATE: 2015-02-20                   -->
<!-- ============================================================== -->
<xsl:transform version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xmlns:fn="http://php.net/xsl" 
	exclude-result-prefixes="fn"
><!-- for fn:func see ex. http://en.wikibooks.org/wiki/PHP_Programming/XSL/registerPHPFunctions  -->

<xsl:output encoding="UTF-8" method="xml" version="1.0" indent="yes" omit-xml-declaration="no"/>

<xsl:parameter name="version">'XX'</xsl:parameter>

<!-- #### MAIN #### -->

<xsl:template match="/">
<xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
<html>
  <head>
    <title>Schema.org master file (version <xsl:value-of select="$version"/>): RDFS in RDFa</title>
    <meta charset="UTF-8" />
    <style type="text/css">
      span.h {
        padding-left: 0px;
        font-weight: bold;
      }
      span {
        display: block;
        padding-left: 10px;
      }
      div.NORMATIVE{background-color:445566;}
    </style>
  </head>

  <body>
    <h1>Schema.org core schema (version <xsl:value-of select="$version"/>)</h1>

    <p>This is the RDFa representation of the schema.org schema, the underlying representation of the schema.org vocabulary.</p>

    <p>It is represented in a form based on W3C RDF/RDFS. We encourage proposals for schema.org improvements to be expressed
      in this same style. For Discussion please use the W3C <a href="mailto:public-vocabs@w3.org">Web schemas</a> group.</p>
    <p>
    See <a href="http://schema.org/docs/datamodel.html">datamodel</a> for more details.
    </p>
    <p>
      Note: the style of RDFa used here may change in the future. To see the substantive content of the schema, view the
      HTML source markup. We use a simple subset of RDFa for syntax, including prefixes that are declared in the
      <a href="http://www.w3.org/2011/rdfa-context/rdfa-1.1">RDFa initial context</a>.
    </p>

    <hr />

	<div class="NORMATIVE">
	<div style="float:right"><small>(normative contentent)</small></div>

	<xsl:foreach select="//div[(@typeof='rdfs:Class' or @typeof='rdf:Property') and ./span/@property='rdfs:label']">
		<div typeof="{$typeof}" resource="{$typeof}">
		<xsl:foreach select="span">
			<span>
				<xsl:if test="@class='h'"><xsl:attribute name="class">h</xsl:attribute></xsl:if>
				<xsl:if test="@property"><xsl:attribute name="property"><xsl:value-of select="@property"/></xsl:attribute></xsl:if>
				<xsl:choose>
					<xsl:when test="@property='rdfs:comment'">
						<xsl:apply-templates mode="comments"/>
					</when>

					<xsl:when test="@property='rdfs:label'"><xsl:value-of select="normalize-space(.)"/></when>
					
					<xsl:when test="./a[@property='rdfs:subClassOf' and contains(./a/@href,'http://schema.org/')]">
						Subclass of: <a property="rdfs:subClassOf" href="{./a/@href}"><xsl:value-of select="substring(./a/@href,20)"/></a><!-- controlled value -->
					</when>
					<xsl:when test="./a[@property='rdfs:subClassOf']"><!-- external href -->
						Subclass of: <a property="rdfs:subClassOf" href="{./a/@href}"><xsl:value-of select="normalize-space(./a/)"/></a><!-- free value -->
					</when>

					<xsl:when test="./a[@property='dc:source']">
						Source: <a property="dc:source" href="{./a/@href}"><xsl:value-of select="normalize-space(./a/)"/></a><!-- free value -->
					</when>

					<xsl:when test="./a[@property='http://schema.org/domainIncludes']">
						Domain: <a property="http://schema.org/domainIncludes" href="{./a/@href}"><xsl:value-of select="normalize-space(./a/)"/></a><!-- free value -->
					</when>

					<xsl:when test="./a[@property='http://schema.org/rangeIncludes'  and contains(./a/@href,'http://schema.org/')]">
						Range: <a property="http://schema.org/rangeIncludes" href="{./a/@href}"><xsl:value-of select="substring(./a/@href,20)"/></a><!-- controlled value -->
					</when>

				</xsl:choose><!-- span contents-->
			</span>
		</xsl:foreach>

		<xsl:foreach select="link">
			<xsl:copy-of select=".">
		</xsl:foreach>

	</xsl:foreach>
	</div><!-- NORMATIVE-->

	<hr/>

	.... Other contents, non-normative....

</xsl:template>


<!-- #### OTHER (text free format): #### -->
<xsl:template match="text()"><xsl:value-of select="."/></xsl:template>
<xsl:template match="i"><i><xsl:apply-templates /></i></xsl:template>
<xsl:template match="b"><b><xsl:apply-templates /></c></xsl:template>

</xsl:transform>

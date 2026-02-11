<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
                xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                exclude-result-prefixes="m w">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <!-- Simple identity transform for math elements to MathML -->
  <xsl:template match="m:oMath">
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <xsl:apply-templates select="*"/>
    </math>
  </xsl:template>

  <xsl:template match="m:r">
    <mrow><xsl:apply-templates select="m:t"/></mrow>
  </xsl:template>

  <xsl:template match="m:t">
    <mtext><xsl:value-of select="."/></mtext>
  </xsl:template>

  <xsl:template match="m:f">
    <mfrac>
      <mrow><xsl:apply-templates select="m:num/*"/></mrow>
      <mrow><xsl:apply-templates select="m:den/*"/></mrow>
    </mfrac>
  </xsl:template>

  <xsl:template match="m:sSub">
    <msub>
      <mrow><xsl:apply-templates select="m:e/*"/></mrow>
      <mrow><xsl:apply-templates select="m:sub/*"/></mrow>
    </msub>
  </xsl:template>

  <xsl:template match="m:sSup">
    <msup>
      <mrow><xsl:apply-templates select="m:e/*"/></mrow>
      <mrow><xsl:apply-templates select="m:sup/*"/></mrow>
    </msup>
  </xsl:template>

  <!-- Fallback for other elements to avoid losing text -->
  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>

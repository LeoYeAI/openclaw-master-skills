#!/usr/bin/env python3
"""
PubMed XML parsing utilities for extracting article metadata
"""

import xml.etree.ElementTree as ET
import json

def parse_pubmed_article(xml_string):
    """
    Parse a single PubMed article from XML
    
    Args:
        xml_string: XML string from PubMed efetch
    
    Returns:
        Dictionary with article metadata
    """
    root = ET.fromstring(xml_string)
    articles = []
    
    for article in root.findall('.//PubmedArticle'):
        data = {}
        
        # PMID
        pmid = article.find('.//PMID')
        data['pmid'] = pmid.text if pmid is not None else None
        
        # Title
        title = article.find('.//ArticleTitle')
        data['title'] = title.text if title is not None else None
        
        # Authors
        authors = []
        for author in article.findall('.//Author'):
            lastname = author.find('LastName')
            forename = author.find('ForeName')
            if lastname is not None:
                name = lastname.text
                if forename is not None and forename.text:
                    name += f" {forename.text[0]}"
                authors.append(name)
        data['authors'] = authors
        
        # First Author Affiliation
        affiliation = article.find('.//AffiliationInfo/Affiliation')
        data['first_affiliation'] = affiliation.text if affiliation is not None else None
        
        # Corresponding Author (usually last author or from affiliation)
        data['corresponding_author'] = authors[-1] if authors else None
        
        # Journal
        journal = article.find('.//Journal/Title')
        data['journal'] = journal.text if journal is not None else None
        
        # Journal Abbreviation
        journal_abbrev = article.find('.//Journal/ISOAbbreviation')
        data['journal_abbrev'] = journal_abbrev.text if journal_abbrev is not None else data['journal']
        
        # Publication Date
        pub_date = article.find('.//PubDate')
        year = None
        month = None
        if pub_date is not None:
            year_elem = pub_date.find('Year')
            month_elem = pub_date.find('Month')
            if year_elem is not None:
                year = year_elem.text
            if month_elem is not None:
                month_text = month_elem.text
                months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                         'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                         'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                month = months.get(month_text, month_text)
        data['year'] = year
        data['month'] = month
        
        # DOI
        doi = None
        for article_id in article.findall('.//ArticleId'):
            if article_id.get('IdType') == 'doi':
                doi = article_id.text
        data['doi'] = doi
        
        # PMC ID
        pmc_id = None
        for article_id in article.findall('.//ArticleId'):
            if article_id.get('IdType') == 'pmc':
                pmc_id = article_id.text
        data['pmc_id'] = pmc_id
        
        # Volume, Issue, Pages
        volume = article.find('.//Journal/JournalIssue/Volume')
        issue = article.find('.//Journal/JournalIssue/Issue')
        pagination = article.find('.//Pagination/MedlinePgn')
        
        data['volume'] = volume.text if volume is not None else None
        data['issue'] = issue.text if issue is not None else None
        data['pages'] = pagination.text if pagination is not None else None
        
        # Abstract (structured with labels)
        abstract_parts = []
        for abstract_text in article.findall('.//Abstract/AbstractText'):
            label = abstract_text.get('Label')
            text = abstract_text.text or ''
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        data['abstract'] = '\n\n'.join(abstract_parts) if abstract_parts else None
        
        articles.append(data)
    
    return articles

def format_gb_reference(article_data):
    """
    Format reference in GB/T 7714-2015 format
    
    Args:
        article_data: Dictionary with article metadata
    
    Returns:
        Formatted reference string
    """
    # Authors (max 3, then et al.)
    authors = article_data.get('authors', [])
    if len(authors) > 3:
        author_str = f"{authors[0]}, {authors[1]}, {authors[2]}, et al."
    else:
        author_str = ", ".join(authors)
    
    # Title
    title = article_data.get('title', '')
    
    # Journal
    journal = article_data.get('journal_abbrev', article_data.get('journal', ''))
    
    # Year, Volume, Issue, Pages
    year = article_data.get('year', '')
    volume = article_data.get('volume', '')
    issue = article_data.get('issue', '')
    pages = article_data.get('pages', '')
    
    # DOI
    doi = article_data.get('doi', '')
    
    # Format: Author. Title[J]. Journal, Year, Volume(Issue): Pages. DOI: xxx.
    ref = f"{author_str}. {title}[J]. {journal}, {year}"
    
    if volume:
        if issue:
            ref += f", {volume}({issue})"
        else:
            ref += f", {volume}"
    
    if pages:
        ref += f": {pages}"
    
    if doi:
        ref += f". DOI: {doi}."
    else:
        ref += "."
    
    return ref

if __name__ == "__main__":
    # Example usage
    sample_xml = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345678</PMID>
                <Article>
                    <ArticleTitle>Sample Article Title</ArticleTitle>
                    <AuthorList>
                        <Author>
                            <LastName>Smith</LastName>
                            <ForeName>John</ForeName>
                        </Author>
                        <Author>
                            <LastName>Doe</LastName>
                            <ForeName>Jane</ForeName>
                        </Author>
                    </AuthorList>
                    <Journal>
                        <Title>Sample Journal</Title>
                        <ISOAbbreviation>Sample J</ISOAbbreviation>
                        <JournalIssue>
                            <Volume>10</Volume>
                            <Issue>2</Issue>
                            <PubDate>
                                <Year>2026</Year>
                                <Month>Mar</Month>
                            </PubDate>
                        </JournalIssue>
                    </Journal>
                    <Pagination>
                        <MedlinePgn>100-110</MedlinePgn>
                    </Pagination>
                    <Abstract>
                        <AbstractText Label="BACKGROUND">Background text.</AbstractText>
                        <AbstractText Label="METHODS">Methods text.</AbstractText>
                        <AbstractText Label="RESULTS">Results text.</AbstractText>
                        <AbstractText Label="CONCLUSION">Conclusion text.</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
            <PubmedData>
                <ArticleIdList>
                    <ArticleId IdType="doi">10.1234/sample.2026</ArticleId>
                </ArticleIdList>
            </PubmedData>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    
    articles = parse_pubmed_article(sample_xml)
    for article in articles:
        print(json.dumps(article, indent=2))
        print("\nGB Reference:", format_gb_reference(article))

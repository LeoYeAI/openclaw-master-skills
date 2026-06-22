#!/usr/bin/env python3
"""
PubMed E-utilities API wrapper for literature search
"""

import urllib.request
import urllib.parse
import json
import time

def search_pubmed(search_term, max_results=100, sort="pub_date"):
    """
    Search PubMed using E-utilities API
    
    Args:
        search_term: Search query (e.g., "gastric neuroendocrine tumor")
        max_results: Maximum number of results to return
        sort: Sort order (pub_date, relevance, author, journal)
    
    Returns:
        List of PMIDs
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    params = {
        "db": "pubmed",
        "term": search_term,
        "retmax": max_results,
        "retmode": "json",
        "sort": sort
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            pmids = data.get("esearchresult", {}).get("idlist", [])
            return pmids
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def fetch_pubmed_details(pmids):
    """
    Fetch detailed information for PMIDs
    
    Args:
        pmids: List of PMIDs (max 200 per request)
    
    Returns:
        XML string with article details
    """
    if not pmids:
        return None
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    # PubMed recommends max 200 IDs per request
    pmid_str = ",".join(pmids[:200])
    
    params = {
        "db": "pubmed",
        "id": pmid_str,
        "retmode": "xml"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode()
    except Exception as e:
        print(f"Error fetching PubMed details: {e}")
        return None

def check_pmc_availability(pmid):
    """
    Check if a PMID has PMC full text available
    
    Args:
        pmid: PubMed ID
    
    Returns:
        PMC ID if available, None otherwise
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    
    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "retmode": "json"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            linksets = data.get("linksets", [])
            if linksets and "linksetdbs" in linksets[0]:
                for linksetdb in linksets[0]["linksetdbs"]:
                    if linksetdb.get("dbto") == "pmc":
                        links = linksetdb.get("links", [])
                        if links:
                            return f"PMC{links[0]}"
        return None
    except Exception as e:
        print(f"Error checking PMC availability: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    pmids = search_pubmed("gastric neuroendocrine tumor", max_results=10)
    print(f"Found {len(pmids)} PMIDs: {pmids}")
    
    if pmids:
        xml = fetch_pubmed_details(pmids[:2])
        print(f"Fetched XML for {len(pmids[:2])} articles")

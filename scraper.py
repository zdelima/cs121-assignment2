import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    try:
        # Assuming the raw response is an HTML page.
        soup = BeautifulSoup(resp.content, "lxml")
        links = soup.find_all("a", href=True)
        
        absolute_links = []
        for link in links:
            href = link["href"]
            full_url = urljoin(url, href)  # Convert relative URLs to absolute URLs
            absolute_links.append(full_url)
        
        return absolute_links
    except Exception as e:
        print(f"Error extracting links: {e}")
        return [] 

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]): # if scheme isnt either http/https
            return False
        if parsed.netloc.endswith(("ics.uci.edu", ".cs.uci.edu", ".information.uci.edu", ".stat.uci.edu")): # if one of the allowed domains
            return True
        if parsed.netloc == "today.uci.edu": # if specifically today.uci.edu
            if parsed.path.startswith("/department/information_computer_sciences/"): # if path correct per assignemnt instructions
                return True
    
        return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise

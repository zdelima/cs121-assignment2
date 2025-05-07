import re
from urllib.parse import urlparse, urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from collections import Counter

unique_pages = set()
longest_page = ("" , 0)
word_frequencies = Counter()
subdomains = Counter()

STOPWORDS = { # stop words based on 
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t',
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t',
    'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t',
    'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his',
    'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s',
    'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t',
    'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s',
    'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll',
    'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t',
    'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where',
    'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t',
    'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

ALLOWED_SUFFIXES = {
    'ics.uci.edu',
    'cs.uci.edu',
    'informatics.uci.edu',
    'stat.uci.edu',
}

ICS_PATH_PREFIX = '/department/information_computer_sciences/'

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
    out = []
    if resp.status != 200 or not hasattr(resp.raw_response, 'content'):
        return out
    try:
        #parse url through beautifulsoup
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    
        defrag_url, _ = urldefrag(url)

        unique_pages.add(defrag_url)
        
        visible_text = soup.get_text(separator=' ', strip=True)
        tokens = re.findall(r'\b\w+\b', visible_text.lower())
                
        if len(tokens) < 200: # if page has low textual information
            return out
        
        filtered_words = [word for word in visible_text if word not in STOPWORDS]

        calculate_stats(filtered_words, url)
        
        for tag in soup.find_all('a', href=True): # get all links
            href = tag['href']
            abs_url = urljoin(resp.url, href)
            clean_url, _ = urldefrag(abs_url)
            out.append(clean_url)
            
    except Exception:
        pass
    return out

def calculate_stats(words, url):
    global longest_page, word_frequencies, subdomains
    
    if len(words) > longest_page[1]: # longest page
        longest_page[0] = url
        longest_page[1] = len(words)
        
    word_frequencies.update(words) # 50 most common words
    
    parsed = urlparse(url)
    if parsed.domain.endswith('.uci.edu'): # subdomains
        Counter[parsed.domain] += 1
        
    make_report()
    
def find_calendar(url):
    calendar_patterns = [
        r'[\?&](month|year|date)=',
        r'/\d{4}/\d{1,2}/?',
        r'/\d{1,2}-\d{1,2}-\d{4}',
        r'/\d{4}-\d{1,2}-\d{1,2}',
    ]
    
    for date in calendar_patterns:
        if re.search(date, url, re.IGNORECASE):
            return True
    return False
        
def find_traps(url):
    parsed = urlparse(url)
    if find_calendar(url):
        return True
    if "doku.php" in parsed.path.lower():
        return True
    if "swiki" in parsed.netloc.lower():
        return True
    if "gitlab" in parsed.netloc.lower():
        return True
    if "~eppstein" in parsed.path.lower():
        return True
    if "grape" in parsed.path.lower():
        return True
    if "eventdate" in parsed.query.lower():
        return True
    if "ical" in parsed.query.lower():
        return True
    if "tribe-bar-date" in parsed.query.lower():
        return True
    if "triube_events_display" in parsed.query.lower():
        return True
    return False

def is_valid(url):
    global unique_pages
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        defrag_url, _ = urldefrag(url)
        
        if defrag_url in unique_pages:
            return False
        else:
            unique_pages.add(defrag_url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|sql|apk|war|img)$", parsed.path.lower()):
            return False
        if not any(parsed.netloc.lower().endswith(suf) for suf in ALLOWED_SUFFIXES) and not (parsed.netloc.lower() == "today.uci.edu" and parsed.path.lower().startswith(ICS_PATH_PREFIX)):
            return False
        if find_traps(url):
            return False
        return True        
    except TypeError:
        print ("TypeError for ", parsed)
        raise
    
def make_report():
    print(f"1. Number of unique pages found: {len(unique_pages)}")
    print(f"2. Longest page in terms of number of words: {longest_page[0]}, {longest_page[1]}")
    print("3. 50 most common words in the entire set of pages:")
    for word, count in word_frequencies.most_common(50):
        print((word, count))
    print("4. Found subdomains:")
    for subdomain, count in subdomains.most_common():
        print((subdomain, count))
        
    with open("report.txt", "w") as f:
        f.write(f"1. Number of unique pages found: {len(unique_pages)}")
        f.write(f"2. Longest page in terms of number of words: {longest_page[0]}, {longest_page[1]}")
        f.write("3. 50 most common words in the entire set of pages:")
        for word, count in word_frequencies.most_common(50):
            f.write((word, count))
        f.write("4. Found subdomains:")
        for subdomain, count in subdomains.most_common():
            f.write((subdomain, count))
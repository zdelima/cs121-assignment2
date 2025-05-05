#!/usr/bin/env python3
import re
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
from utils.response import Response

seen_urls = set()
page_word_counts = {}
word_freq = Counter()
subdomain_counts = defaultdict(int)

STOPWORDS = {
    'a','about','above','after','again','against','all','am','an','and','any','are','aren't',
    'as','at','be','because','been','before','being','below','between','both','but','by',
    'can't','cannot','could','couldn't','did','didn't','do','does','doesn't','doing','don't',
    'down','during','each','few','for','from','further','had','hadn't','has','hasn't','have','haven't',
    'having','he','he'd','he'll','he's','her','here','here's','hers','herself','him','himself','his',
    'how','how's','i','i'd','i'll','i'm','i've','if','in','into','is','isn't','it','it's',
    'its','itself','let's','me','more','most','mustn't','my','myself','no','nor','not','of','off',
    'on','once','only','or','other','ought','our','ours','ourselves','out','over','own','same','shan't',
    'she','she'd','she'll','she's','should','shouldn't','so','some','such','than','that','that's',
    'the','their','theirs','them','themselves','then','there','there's','these','they','they'd','they'll',
    'they're','they've','this','those','through','to','too','under','until','up','very','was','wasn't',
    'we','we'd','we'll','we're','we've','were','weren't','what','what's','when','when's','where',
    'where's','which','while','who','who's','whom','why','why's','with','won't','would','wouldn't',
    'you','you'd','you'll','you're','you've','your','yours','yourself','yourselves'
}

ALLOWED_SUFFIXES = (
    '.ics.uci.edu',
    '.cs.uci.edu',
    '.informatics.uci.edu',
    '.stat.uci.edu'
)
ICS_PATH_PREFIX = '/department/information_computer_sciences/'

BAD_EXTENSIONS = re.compile(
    r'.*\.(css|js|bmp|gif|jpe?g|png|svg|ico|tiff?|mid|mp2|mp3'
    r'|mp4|wav|avi|mov|mpeg|ram|m4v|pdf|docx?'
    r'|xlsx?|pptx?|zip|rar|gz)$',
    re.IGNORECASE
)

MAX_PATH_SEGMENTS = 30
MAX_NUMERIC_RUN = 3

def is_valid(url: str) -> bool:
    try:
        clean, _ = urldefrag(url)
        parsed = urlparse(clean)
        scheme = parsed.scheme.lower()
        host = parsed.netloc.lower()
        path = parsed.path

        if scheme not in ('http', 'https'):
            return False
        if BAD_EXTENSIONS.match(path.lower()):
            return False

        segments = [seg for seg in path.split('/') if seg]
        if len(segments) > MAX_PATH_SEGMENTS:
            return False
        run = 0
        for seg in segments:
            if seg.isdigit():
                run += 1
                if run >= MAX_NUMERIC_RUN:
                    return False
            else:
                run = 0

        if any(host.endswith(suf) for suf in ALLOWED_SUFFIXES):
            return True
        if host == 'today.uci.edu' and path.lower().startswith(ICS_PATH_PREFIX):
            return True
        return False
    except Exception:
        return False

def extract_next_links(url: str, resp: Response) -> list:
    out = []
    if resp.status != 200 or not hasattr(resp.raw_response, 'content'):
        return out
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            abs_url = urljoin(resp.url, href)
            clean_url, _ = urldefrag(abs_url)
            out.append(clean_url)
    except Exception:
        pass
    return out

def extract_tokens(resp: Response) -> list:
    tokens = []
    if resp.status != 200 or not hasattr(resp.raw_response, 'content'):
        return tokens
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    text = ' '.join(soup.stripped_strings)
    for word in re.findall(r'\w+', text.lower()):
        if word not in STOPWORDS:
            tokens.append(word)
    return tokens

def scraper(url: str, resp: Response) -> list:
    if resp.status != 200:
        return []
    content_type = resp.raw_response.headers.get('Content-Type', '').lower()
    if 'text/html' not in content_type:
        return []
    clean_page, _ = urldefrag(resp.url)
    if clean_page not in seen_urls:
        seen_urls.add(clean_page)
        host = urlparse(clean_page).netloc.lower()
        subdomain_counts[host] += 1
        tokens = extract_tokens(resp)
        page_word_counts[clean_page] = len(tokens)
        word_freq.update(tokens)
    raw_links = extract_next_links(url, resp)
    return [link for link in raw_links if is_valid(link)]

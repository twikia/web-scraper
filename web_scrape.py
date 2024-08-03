import requests
from bs4 import BeautifulSoup
import validators
import re
from urllib.parse import urlparse, urljoin
import time
from requests_html import HTMLSession
from Wappalyzer import Wappalyzer, WebPage
import warnings
from newspaper import Article
import pandas as pd
import sys
# import nltk
# nltk.download('punkt')


def get_read_speed(wordcount, read_speed=238):
    mins = wordcount / read_speed
    seconds = int((mins % 1) * 60)
    mins = int(mins // 1)
    
    return mins, seconds



def detect_tech_stack(url):
    """Attempts to detect the web server, CMS, and JavaScript libraries used by a website."""
    try:

        webpage = WebPage.new_from_url(url)
        wappalyzer = Wappalyzer.latest()
        return wappalyzer.analyze_with_versions_and_categories(webpage)
        # return wappalyzer.analyze(webpage)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website: {e}")
        return {}



def categorize_links(soup, base_url):
    """Categorizes links into external and internal based on the base URL."""
    external_links = []
    internal_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Resolve relative URLs
        full_url = urljoin(base_url, href) 
        parsed_url = urlparse(full_url)
        if parsed_url.netloc == '' or parsed_url.netloc == urlparse(base_url).netloc:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)
    return external_links, internal_links



def scrape_contact_info(soup):

    contact_info = {
        'emails': [],
        'phones': [],
        'socials': {}
    }

    # Extract Emails
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    contact_info['emails'] = re.findall(email_pattern, soup.get_text())

    # Extract Phone Numbers (adjust pattern as needed for your region)
    phone_pattern = r"\(?\b[2-9][0-9]{2}\)?[-.\s][2-9][0-9]{2}[-.\s][0-9]{4}\b"
    contact_info['phones'] = re.findall(phone_pattern, soup.get_text())

    # Extract Social Media Links
    social_media_links = soup.find_all('a', href=True)
    for link in social_media_links:
        href = link['href']
        parsed_url = urlparse(href)
        for platform in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']:
            if platform in parsed_url.netloc:
                contact_info['socials'][platform] = href

    return contact_info



def summarize_ai(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return str(article.summary)



def extract_website_info(soup):
    """Fetches and extracts website information, handling potential variations."""

    info = {}  # Dictionary to store extracted information

    # Title (most reliable, usually present)
    info['title'] = soup.find('title').get_text() if soup.find('title') else None

    # Meta Tags (flexible search)
    for tag in soup.find_all('meta'):
        name = tag.get('name', '').lower()  # Get name, case-insensitive
        property = tag.get('property', '').lower()  # Get property, case-insensitive
        content = tag.get('content')

        if name == 'description':
            info['description'] = content
        elif name == 'keywords':
            info['keywords'] = content
        elif property == 'og:title':  # Open Graph title (fallback)
            info['og_title'] = content
        elif property == 'og:description':  # Open Graph description (fallback)
            info['og_description'] = content
        # ... Add more checks for other meta properties you want ...

    # Publish/Modify Dates (heuristic search)
    for tag in soup.find_all(['time', 'span', 'meta']):
        datetime = tag.get('datetime')
        if datetime:
            # Check for common patterns (you might need to adjust these)
            if 'pub' in tag.get('class', []) or 'published' in tag.get_text().lower():
                info['publish_date'] = datetime
            elif 'mod' in tag.get('class', []) or 'modified' in tag.get_text().lower():
                info['modify_date'] = datetime
    
    return info



def get_structure(soup):
    
    # Heading Structure
    heading_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "div", "p", "style"]  # Consider h1 most important
    heading_counts = {}
    for tag in heading_tags:
        heading_counts[tag] = len(soup.find_all(tag))
        
    raw_html = str(soup)
    # link_count = len(re.findall(r'<a\s+[^>]*href\s*=', raw_html))
    # links = [a['href'] for a in soup.find_all('a', href=True)]

    # Media Count (Images, Videos, Audio)
    img_count = len(soup.find_all("img"))
    video_count = len(soup.find_all("video"))
    audio_count = len(soup.find_all("audio"))

    temp_dic =  {
        "image_count": img_count,
        "video_count": video_count,
        "audio_count": audio_count,
        # "link_count": link_count,
    }
    
    return temp_dic | heading_counts



def get_user_url():
    try:
        url = str(input("Provide a URL to analyze:\n"))
        if not validators.url(url):
            print("Provide a valid URL.\n")
            return get_user_url()
    except:
        return get_user_url()
        
    return url
        


def get_show_links(all_links, external_links, internal_links):
    
    if not all_links:
        return
    
    
    try:
        response = str(input("\nWould you like to see links I(internal), E(external), A(all), any-key(skip)?"))
    
        if response in ["I", "i"]:
            for indx, i in enumerate(internal_links, start=1):
                print(indx, ": ", i)
            
        if response in ["E", "e"]:
            for indx, i in enumerate(external_links, start=1):
                print(indx, ": ", i)
            
        if response in ["A", "a"]:
            for indx, i in enumerate(all_links, start=1):
                print(indx, ": ", i)
    except:
        pass



def get_website_performance_metrics(url):
    
    session = HTMLSession()
    
    # Initial Load Metrics
    start_time = time.time()
    try:
        r = session.get(url, timeout=4)
        initial_load_time = time.time() - start_time
    
        r.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(e)
        return None, None
    
    metrics = {
        'page_load_time': round(initial_load_time,6),
        'http_status_code': r.status_code,
        'num_requests': len(r.html.links),  
        'page_size_bytes': len(r.content)
    }

    # Render Page (including JavaScript)
    # render_start_time = time.time()
    # r.html.render()
    # render_end_time = time.time()

    # # Rendered Page Metrics
    # metrics['whole_page_render_time'] = render_end_time - render_start_time + initial_load_time  # Total time including initial load
    # metrics['whole_page_num_requests'] = len(r.html.links)  
    # metrics['whole_page_size'] = len(r.html.html) 

    return metrics, soup



def get_word_count(soup):
    text = soup.get_text()  
    words = text.split()  
    word_count = len(words)
    return word_count



def show_results(dic):
    
    skip_list = ["External links", "Internal links", "All links"]
    space_list = ["Summary", "emails", "Num Links", "Word_count"]
    print("\nRESULTS: \n")
    
    for key in dic.keys():
        if key in skip_list:
            continue        
        if key in space_list:
            print(" ")            
        print(f"{key}: {dic[key]}")
    
    
    
def concat_dfs(df1, df2):
    df1.drop(['Index'], axis=1, inplace=True)
    concatted = pd.concat([df1, df2])
    concatted.drop_duplicates(inplace=True, subset=["URL"], keep="first", ignore_index=True)
    concatted.reindex()
    concatted.index.name = "Index"
    
    return concatted

    
    
def main(url="https://en.wikipedia.org/wiki/Web_scraping"):
    
    # Filter out the specific warning
    warnings.filterwarnings("ignore", message="Caught 'unbalanced parenthesis at position 119' compiling regex", category=UserWarning)
    
    
    metrics = {
        "URL":url
    }
    
    perf, soup = get_website_performance_metrics(url)
    
    if not perf:
        return None
    
    
    metrics = metrics | perf
    
    word_count = get_word_count(soup)
    metrics["Word_count"] = word_count
    
    read_time = get_read_speed(word_count)
    metrics["Read_time"] = f"Mins: {read_time[0]}, Sec: {read_time[1]}"
    
    metrics = metrics | extract_website_info(soup)
    metrics["Summary"] = summarize_ai(url)
    
    external_links, internal_links = categorize_links(soup, url)
    metrics["Num Links"] = len(external_links) + len(internal_links)
    metrics["Num External links"] = len(external_links)
    metrics["Num Internal links"] = len(internal_links)
    
    struct = get_structure(soup)
    metrics = metrics | struct
    metrics = metrics | scrape_contact_info(soup)
    metrics = metrics | detect_tech_stack(url)
    
    metrics["External links"] = external_links
    metrics["Internal links"] = internal_links
    
    return metrics



if __name__ == "__main__":
    
    url = get_user_url()
    met = main(url) 
    if not met:
        print("Bad URL")
        sys.exit(0)
    
    show_results(met)
    get_show_links(met["External links"] + met["Internal links"], met["External links"], met["Internal links"])
    
    df = pd.DataFrame([met])
    df = concat_dfs(pd.read_csv("history//your-websites.csv"), df)
    df.to_csv("history//your-websites.csv")
    
    
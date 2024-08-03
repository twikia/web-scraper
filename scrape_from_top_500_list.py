import requests
from bs4 import BeautifulSoup
import scape_url_list
import re


def get_links_with_class(url, class_name="ml-2"):
    """Fetches a webpage and returns a list of links with the specified class.

    Args:
        url (str): The URL of the webpage to scrape.
        class_name (str, optional): The class name to search for (default: "ml-2").

    Returns:
        list: A list of links (href attributes) found on the page that have the specified class.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    links = []
    for link in soup.find_all('a', class_=class_name):
        links.append(link.get('href'))  

    return links



def scrape_www_links_from_html(url):
    """Scrapes a webpage's HTML and returns a list of links starting with 'www.'

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        list: A list of URLs found in the HTML that start with 'www.'.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')


    # Find all occurrences of "www." in the HTML
    www_matches = soup.find_all(string=re.compile(r'www\.'))

    links = []
    for match in www_matches:
        # Extract the part of the string after 'www.' until the next '<'
        link_match = re.search(r'www\.([^</td>]+)', str(match))
        if link_match:
            links.append('www.' + link_match.group(1))

    return links



def main(url="https://www.zyxware.com/articles/4344/list-of-fortune-500-companies-and-their-websites", class_name="ml-2"):
    # url_list = get_links_with_class(url, class_name)
    
    url_list = scrape_www_links_from_html(url)
    url_list = ["https://" + domain for domain in url_list]
    print(len(url_list))
    # print(url_list)
    
    scape_url_list.scrape_url_list(url_list, "from_t500_list")
    # df.to_csv("history//from_t500_list.csv")
    # df.to_feather("history//from_t500_list.feather")
    
    

if __name__ == "__main__":
    main()

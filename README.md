# web-scraper
Technical information about websites along with a short summary. Mostly things you can't see when browsing a website.


# how to use
- web_scrape: enter in a url and it will print out results. It will also append you results into the your-websites.csv (please download libraries, also uncommenting lines 13-14 might be nessesary first time running).
  
- scrape_url_list: this goes through all the companies on the helpers/websites.csv. If you want it to go through helpers/url_list.csv uncomment the two functions that are commented and comment the two that are active.
  
- scrape_from_top_500: this function finds all urls beggining with www. and then end with \&lt;/td> . Originally it was meant to scrape all with a certain html class for the links but first website didn't allow scraping.

# feel free to modify to your own code and suggest any changes! Enjoy!

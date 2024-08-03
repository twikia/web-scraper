import pandas as pd
import web_scrape 
import pyarrow.feather as feather
import time




def combine_dfs(df1, df2):
    concatted = pd.concat([df1, df2])
    concatted.drop_duplicates(inplace=True, subset=["URL"], keep="first", ignore_index=True)
    concatted.reindex()
    return concatted



def scrape_url_list(url_list, file_name="from_url_list"):
    res = None
    indx = 0
    while not res and indx < len(url_list):
        res = web_scrape.main(url_list[indx])
        indx += 1
        
        
    df = pd.DataFrame([res])
    for i in range(1, len(url_list)):
        try:
            start_time = time.perf_counter()
            print(i, ": ", url_list[i])
            result = web_scrape.main(url_list[i])
            if not result:
                print(f"{url_list[i]}, failed")
                continue
            
            
            df = combine_dfs(df, pd.DataFrame([result]))
            
            # for saving to files called websites
            df.to_csv(f"history//{file_name}.csv")
            df.to_feather(f"history//{file_name}.feather")
            print(time.perf_counter() - start_time)
            
        except Exception as e:
            print(e)
            
        time.sleep(1)
        
    return df



def main():
    
    # this line reads from the url list file
    # url_list = pd.read_csv("helpers//url_list.csv")["URL"].tolist()
    
    # this code reads from the websites.csv file
    url_list = pd.read_csv("helpers//websites.csv")["URL"].tolist()
    url_list = ["https://www." + domain for domain in url_list]
    
    
    # save to website filename
    scrape_url_list(url_list, "from_websites_list")
    
    # for saving to url list
    # scrape_url_list(url_list)
    
    
    
    
    
    
if __name__ == "__main__":
    main()
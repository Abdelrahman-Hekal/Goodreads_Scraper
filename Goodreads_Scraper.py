from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService 
import undetected_chromedriver as uc
import pandas as pd
import time
import csv
import sys
import numpy as np
import re 

def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options  = webdriver.ChromeOptions()
    # suppressing output messages from the driver
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    # adding user agents
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # running the driver with no browser window
    #chrome_options.add_argument('--headless')
    # disabling images rendering 
    #prefs = {"profile.managed_default_content_settings.images": 2}
    #chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.page_load_strategy = 'normal'
    # installing the chrome driver
    driver_path = ChromeDriverManager().install()
    chrome_service = ChromeService(driver_path)
    # configuring the driver
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    driver.set_page_load_timeout(10000)
    driver.maximize_window()

    return driver

def scrape_goodreads(path):

    start = time.time()
    print('-'*75)
    print('Scraping goodreads.com ...')
    print('-'*75)
    # initialize the web driver
    driver = initialize_bot()

    # initializing the dataframe
    data = pd.DataFrame()

    # if no books links provided then get the links
    if path == '':
        name = 'goodreads_data.xlsx'
        # getting the books under each category
        links = []
        nbooks = 0
        homepages = ['https://www.goodreads.com/list/show/1.Best_Books_Ever?page=', 'https://www.goodreads.com/list/show/47.Best_Dystopian_and_Post_Apocalyptic_Fiction?page=', 'https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once?page=', 'https://www.goodreads.com/list/show/8166.Books_You_Wish_More_People_Knew_About?page=', 'https://www.goodreads.com/list/show/11.Best_Crime_Mystery_Books?page=', 'https://www.goodreads.com/list/show/19.Best_for_Book_Clubs?page=', 'https://www.goodreads.com/list/show/1736.Best_Teen_Books_About_Real_Problems?page=', 'https://www.goodreads.com/list/show/497.The_Most_Begun_Read_but_Unfinished_Started_book_ever?page=', 'https://www.goodreads.com/list/show/134.Best_Non_Fiction_no_biographies_?page=', 'https://www.goodreads.com/list/show/281.Best_Memoir_Biography_Autobiography?page=', 'https://www.goodreads.com/list/show/1083.The_Most_Influential_Books?page=', 'https://www.goodreads.com/list/show/143.Favorite_Magical_Realism_Novels?page=', 'https://www.goodreads.com/list/show/946.Books_Besides_the_Bible_Recommended_for_Christian_Readers?page=', 'https://www.goodreads.com/list/show/692.Best_Science_Books_Non_Fiction_Only?page=', 'https://www.goodreads.com/list/show/1362.Best_History_Books_?page=', 'https://www.goodreads.com/list/show/1371.Recommended_Historical_Fiction?page=', 'https://www.goodreads.com/list/show/7616.Motivational_and_Self_Improvement_Books?page=', 'https://www.goodreads.com/list/show/453.Best_Philosophical_Literature?page=', 'https://www.goodreads.com/list/show/1720.Well_Written_Holocaust_Books?page=']

        for homepage in homepages:
            for i in range(1,4):
                url = homepage + str(i)
                driver.get(url)
                # scraping books urls
                titles = wait(driver, 2).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
                for title in titles:
                    try:
                        nbooks += 1
                        print(f'Scraping the url for book {nbooks}')
                        link = wait(title, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.bookTitle"))).get_attribute('href')
                        links.append(link)
                    except Exception as err:
                        print('The below error occurred during the scraping from goodreads.com, retrying ..')
                        print('-'*50)
                        print(err)
                        continue
                    
        # saving the links to a csv file
        print('-'*75)
        print('Exporting links to a csv file ....')
        with open('goodreads_links.csv', 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Link'])
            for row in links:
                writer.writerow([row])

    scraped = []
    if path != '':
        df_links = pd.read_csv(path)
        name = path.split('\\')[-1][:-4]
        name = name + '_data.xlsx'
    else:
        df_links = pd.read_csv('goodreads_links.csv')

    links = df_links['Link'].values.tolist()

    try:
        data = pd.read_excel(name)
        scraped = data['Title Link'].values.tolist()
    except:
        pass

    # scraping books details
    print('-'*75)
    print('Scraping Books Info...')
    print('-'*75)
    n = len(links)
    for i, link in enumerate(links):
        try:
            if link in scraped: continue
            driver.get(link)           
            details = {}
            print(f'Scraping the info for book {i+1}\{n}')

            # closing sign in window
            try:
                div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.Overlay__window")))
                button = wait(div, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='Button Button--transparent Button--small Button--rounded']")))
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except:
                pass            
                
            try:
                div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal__content")))
                button = wait(div, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='gr-iconButton']")))
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except:
                pass
            # title and title link
            title_link, title = '', ''              
            try:
                title_link = link
                title = wait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).get_attribute('textContent').replace('\n', '').strip().title() 
            except:
                print(f'Warning: failed to scrape the title for book: {link}')               
                
            details['Title'] = title
            details['Title Link'] = title_link                          
            # Author and author link
            author, author_link = '', ''
            try:
                div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ContributorLinksList")))
                tags = wait(div, 2).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                for tag in tags:
                    author_link += tag.get_attribute('href') + ', '
                    author += tag.get_attribute('textContent') + ', '

                details['Author'] = author[:-2]            
                details['Author Link'] = author_link[:-2]
            except Exception as err:
                pass

            # Rating
            rating = ''
            try:
                rating = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.RatingStatistics__rating"))).get_attribute('textContent').strip()
            except:
                pass          
                
            details['Rating'] = rating            
            
            # Number of ratings
            nratings = ''
            try:
                nratings = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='ratingsCount']"))).get_attribute('textContent').replace('ratings', '').replace(',', '').strip()
            except:
                pass          
                
            details['Number of Ratings'] = nratings           
                               
            # number of reviews
            nrevs = ''
            try:
                nrevs = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='reviewsCount']"))).get_attribute('textContent').replace('reviews', '').replace(',', '').strip()
            except:
                pass          
                
            details['Number of Reviews'] = nrevs 
            
            # genres
            genres = ''
            try:
                spans = wait(driver, 2).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.BookPageMetadataSection__genreButton")))
                for span in spans:
                    genres += span.get_attribute('textContent') + ', '

                details['Genres'] = genres[:-2]   
            except:
                pass          
                
                                             
            # format and number of pages
            form, npages = '', ''
            try:
                p = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-testid='pagesFormat']"))).get_attribute('textContent')
                elems = p.split(',')
                for elem in elems:
                    if 'pages' in elem:
                        npages = elem.split(' ')[0]
                    else:
                        form = elem.strip()
            except:
                pass          
                
            details['Format'] = form              
            details['Number of Pages'] = npages   
 
            # publication date
            date = ''
            try:
                date = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-testid='publicationInfo']"))).get_attribute('textContent').replace('First', '').replace('published', '').replace('Published', '').strip()
            except:
                pass          
                
            details['Publication Date'] = date             
            
            # stars percents
            five, four, three, two, one = '', '', '', '', ''
            try:
                div = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='RatingsHistogram RatingsHistogram__interactive']")))
                scores = wait(div, 2).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='RatingsHistogram__labelTotal']")))
                five = scores[0].get_attribute('textContent').split('(')[-1]
                four = scores[1].get_attribute('textContent').split('(')[-1]
                three = scores[2].get_attribute('textContent').split('(')[-1]
                two = scores[3].get_attribute('textContent').split('(')[-1]
                one = scores[4].get_attribute('textContent').split('(')[-1]

                details['5-stars %'] = five[:-2]          
                details['4-stars %'] = four[:-2] 
                details['3-stars %'] = three[:-2]           
                details['2-stars %'] = two[:-2]  
                details['1-star %'] = one[:-2]  
            except:
                pass          
                
            # Amazon Link
            Amazon = ''
            try:
                button = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='Button Button--buy Button--medium Button--block']")))
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                Amazon = driver.current_url
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                if 'www.amazon' not in Amazon:
                    Amazon = ''
            except:
                pass          
                
            details['Amazon Link'] = Amazon  

            # appending the output to the datafame       
            data = data.append([details.copy()])
            # saving data to csv file each 100 links
            if np.mod(i+1, 100) == 0:
                print('Outputting scraped data ...')
                data.to_excel(name, index=False)
        except Exception as err:
            print(str(err))
            driver.quit()
            driver = initialize_bot()

    # optional output to excel
    data.to_excel(name, index=False)
    elapsed = round((time.time() - start)/60, 2)
    print('-'*75)
    print(f'goodreads.com scraping process completed successfully! Elapsed time {elapsed} mins')
    print('-'*75)
    driver.quit()

    return data

if __name__ == "__main__":
    
    path = ''
    if len(sys.argv) == 2:
        path = sys.argv[1]
    data = scrape_goodreads(path)


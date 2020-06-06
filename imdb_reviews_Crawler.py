import re
import requests
import time
import csv
from selenium import webdriver
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def generate_movie_list_link(i):
    movie_list_url = "https://www.imdb.com/search/title/?title_type=tv_movie&release_date=2010-01-01,2019-01-01&sort=num_votes,desc&start="+str((i-1)*50+1)+"&ref_=adv_nxt"
    return  movie_list_url

def generate_movie_review_list_link(url):
    URL = url
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html,'lxml')
            movies = soup.select('.lister-item-content')
            movie_reviews_url_list = [[0] * 2 for j in range(50)]
            i = 0
            for movie in movies:
                header = movie.select_one('.lister-item-header')
                movie_link = header.select_one('a')['href']
                id_pattern = re.compile(r'(?<=tt)\d+(?=/?)')
                movie_id = int(id_pattern.search(movie_link).group())
                movie_reviews_url = "https://www.imdb.com/title/tt"+str(movie_id)+"/reviews?spoiler=hide&sort=helpfulnessScore&dir=desc&ratingFilter=0"

                movie_reviews_url_list[i] = [movie_id,movie_reviews_url]
                i += 1
                #print(i,movie_id,movie_reviews_url)
                #time.sleep(1)
            return movie_reviews_url_list
        else:
            print("Error when request URL")
    except RequestException:
        print("Request Failed")
        return None


def get_imdb_movie_review(url,movieId):
    NETWORK_STATUS = True
    URL = url
    print(URL)
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            original_html = response.text
            original_soup = BeautifulSoup(original_html,'lxml')
            driver = webdriver.Firefox(executable_path='C:\\Program Files\\Mozilla Firefox\\geckodriver.exe')
            driver.get(URL)

            while(1):
                temp_response = driver.page_source
                temp_html = temp_response
                temp_soup = BeautifulSoup(temp_html,'lxml')
                load_more = temp_soup.select('.ipl-load-more__button')

                if(len(load_more) == 1):
                    button_load_more = driver.find_element_by_class_name('ipl-load-more__button')
                    button_is_or_not_visible = driver.find_element_by_class_name('ipl-load-more__button').is_displayed()
                    if(button_is_or_not_visible is True):
                        button_load_more.click()
                        time.sleep(1)
                    else:
                        break
                else:
                    break

            final_response = driver.page_source
            html = final_response
            soup = BeautifulSoup(html,'lxml')

            movie_id = movieId
            reviews = soup.select('.review-container')
            movie_reviews_list = [[0] * 4 for j in range(1000)]

            i = 0
            for review in reviews:
                header = review.select_one('.display-name-date')
                user_link = header.select_one('a')['href']
                user_id_pattern = re.compile(r'(?<=ur)\d+(?=/?)')
                user_id = int(user_id_pattern.search(user_link).group())    #id
                review_date = header.select_one('.review-date').string      #time

                content = review.select_one('.content')
                user_review = content.select('.text.show-more__control')     #review
                movie_reviews_list[i][0] = user_id
                movie_reviews_list[i][1] = review_date
                movie_reviews_list[i][2] = user_review
                movie_reviews_list[i][3] = movie_id

                i += 1
                #print(i,user_id,review_date,user_review,movie_id)
                time.sleep(0.1)

            driver.close()      #close
            return movie_reviews_list
        else:
            print("Error when request URL")
    except RequestException:
        print("Request Failed")
        return None
    except requests.exceptions.Timeout:
        NETWORK_STATUS = False
        if NETWORK_STATUS == False:
            driver.close()
            print('request timeout')
            get_imdb_movie_review(URL, movieId)

if __name__ == '__main__':
    i = 0
    count = 0
    with open('movie_review_info.csv', 'w', newline="",encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, dialect=("excel"))
        csvwriter.writerow(["userId", "reviewDate", "userReview","movieId"])

        print("Page No." + str(i+1) )
        movie_list_url = generate_movie_list_link(i + 1)
        movie_review_url_list =  generate_movie_review_list_link(movie_list_url)
        j = 0

        while (j < 5):
            print("Review of Movie No." + str(i * 50 + j + 1) )
            l = [[0] * 4 for j in range(1000)]
            l = get_imdb_movie_review(movie_review_url_list[j][1], movie_review_url_list[j][0])
            k = 0
            if(l is None):
                j += 1
                continue

            while(l[k][0] != 0):
                csvwriter.writerow(l[k])
                k += 1
                count += 1
            j += 1


    print("Finished，Get"+str(count)+"reviews")

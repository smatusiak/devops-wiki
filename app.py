'''
Create a Jekyll blog that takes a category/theme and starting question.
The application then:
- performs a Google search based on the question
- get the "people also ask" questions
- for all the questions
    - perform a Google search
    - scrape the results
    - save the results to a file
- take all files and group by similarity
- for each group
    - feed to OpenAI GPT-3 to generate a post complete with
        - title
        - excerpt
        - tl;dr
        - intro
        - details
        - conclusion
        - references
        - tags
        - cheat sheet
    - save the post to a markdown file
'''

import BeautifulSoup
import requests
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

import os
import openai

def get_search_results(question):
    '''
    Perform a Google search
    params:
        question - the question to search for
    returns:
        list of search results
    '''
    # perform a Google search
    url = "https://www.google.com/search?q=" + question
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='g')

    # return the search results
    return results

# get the "people also ask" questions
def get_people_also_ask(question):
    '''
    Get the "people also ask" questions from Google
    params:
        question - the question to search for
    returns:
        list of questions
    '''

    # perform a Google search
    search_results = get_search_results(question)

    # get the "people also ask" questions
    people_also_ask = [question]
    for result in search_results:
        # append question text to list
        people_also_ask += result.find_all('div', class_='Z0LcW').text
        

    # return the "people also ask" questions
    return people_also_ask

# scrape the results
def scrape_results(search_results):
    '''
    Scrape the search results
    params:
        search_results - the search results to scrape
    returns:
        dataframe of scraped results with url, content, and title
    '''

    #pandas dataframe to store results
    df = pd.DataFrame(columns=['url', 'content', 'title'])
    # scrape the results
    for result in search_results:
        # get url
        url = result.find('a')['href']
        title = result.find('title').text

        # scrape page including h1, h2, h3, h4, p, li, ul, ol
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get content
        scraped_result = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'ul', 'ol'])
        # concatenate content
        content = ' '.join([result.text for result in scraped_result])


        for result in scraped_result:
            df = df.append({'url': url, 'content': content}, ignore_index=True)
        
    # return the scraped results
    return df

# save the results to a file
def save_results(scraped_results, question):
    '''
    Save the scraped results to a file
    params:
        scraped_results - dataframe containing scraped results training data
        question - the question to save the results for
        category - the theme of the blog
    returns:
        None
    '''
    # save the results to a file
    scraped_results.to_csv(theme = ': ' + question + '.csv', index=False)


# generate blog content
def generate_blog_content(df):
    '''
    Send scraped results to OpenAI GPT-3 to generate blog content
    params:
        df - dataframe containing scraped results training data
    returns:
        blog content
    '''

    # load api key from dotenv
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # concatenate all content from dataframe
    content = ' '.join(df['content'])

    # create prompt intro
    prompt_intro = 'Create 10 blog posts. Use the below as training data. Format the posts in Markdown using <---> as the page end. Include the following content including:\n- title\n- excerpt\n- tl;dr\n- intro\n- details\n- conclusion\n- references\n- tags\n- cheat sheet\n\n'
    # send content to OpenAI GPT-3
    response = openai.Completion.create(
        model = 'text-davinci-003',
        prompt = prompt_intro + content,
        temperature = 0.9,
        max_tokens = 4000,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0
    )
    





    
# main function for user input - question, category, theme
def main():
    '''
    get user input
    check if data file exists
    if not, get question, category, and theme and create data file
    if yes, load csv into dataframe and generate blog
    '''
    question = input("Have you generated a data file? (y/n) ")

    if question == 'y':
        # ask user for filename
        filename = input("What is the filename? ")
        # load csv into dataframe
        df = pd.read_csv(filename)

    elif question == 'n':
        question = input("What is your question? ")
        theme = input("What is the theme? ")

        # get the "people also ask" questions
        people_also_ask = get_people_also_ask(question)

        # for each question
        for question in people_also_ask:
            # perform a Google search
            search_results = get_search_results(question)

            # scrape the results
            df = scrape_results(search_results)

        # save the results to a file
        save_results(df, question, theme)
    
    # generate blog content
    blog_content = generate_blog_content(df)

    # generate blog files
    generate_blog_files(blog_content)



    

    # take all files and group by similarity

    # for each group
        # feed to OpenAI GPT-3 to generate a post complete with
            # title
            # excerpt
            # tl;dr
            # intro
            # details
            # conclusion
            # references
            # tags
            # cheat sheet

        # save the post to a markdown file


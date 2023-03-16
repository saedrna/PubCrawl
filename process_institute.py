import pandas as pd
import glob
import argparse
import os
import numpy as np
from chatgpt_wrapper import ChatGPT

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Process the institute data, encode with geographic coordinates")
    parser.add_argument('-i' , '--input', type=str, required=True, help='Path to the csv data directory')
    parser.add_argument('-o' , '--output', type=str, required=True, help='Path to the output file')
    parser.add_argument('--api', type=str, required=True, help='API Key for chat-gpt')
    args = parser.parse_args()
    os.environ['OPENAI_API_KEY']=args.api
    input_path = args.input
    output_path = args.output


    # get the csv file in the input directory
    paths = glob.glob(os.path.join(input_path, '*.csv'))

    # read the csv file into pandas dataframe
    data_column = ['title', 'first author', 'corr author', 'inst1', 'inst2',
                'inst3', 'inst4', 'inst5', 'kw1', 'kw2', 'kw3', 'kw4', 'kw5']
    df = pd.DataFrame(columns=data_column)
    for path in paths:
        # the csv data has header
        df = df.append(pd.read_csv(path, header=0, names=data_column))
    
    # create an array to store all institutes
    institutes = np.array([])
    
    # extracts all institutes, which are not null
    for i in range(1, 5):
        institutes = np.append(institutes, df['inst{}'.format(i)].dropna().unique())
    institutes = np.unique(institutes)

    # encode the institutes with geographic coordinates
    encode_column = ['inst', 'lat', 'lon', 'university', 'city', 'country']
    encode_df = pd.DataFrame(columns=encode_column)
    
    bot = ChatGPT()
    for inst in institutes:
        # use chat-gpt
        prompt = f'Please tell me the information of "{inst}" in the following format: "latitude, longitude, university, city, country"'
        success, response, message = bot.ask(prompt)
        if success:
            # parse the response
            response = response.split(',')
        else:
            raise RuntimeError(message)


    


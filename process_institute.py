import argparse
import glob
import json
import os

import numpy as np
import openai
import pandas as pd

os.environ['HTTP_PROXY'] = "http://127.0.0.1:10809"
os.environ['HTTPS_PROXY'] = "http://127.0.0.1:10809"

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Process the institute data, encode with geographic coordinates")
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the csv data directory')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output file')
    parser.add_argument('--api', type=str, required=True, help='API Key for chat-gpt')
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output
    openai.api_key = args.api

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

    example = {
        "Latitude": 30.2849,
        "Longitude": -97.7341,
        "Name": "University of Texas at Austin",
        "City": "Austin",
        "Country": "USA"
    }
    # dump exmaple dict into json string
    example = json.dumps(example)

    messages = [
        {"role": "user",
         "content": "Please get the information of 'Univ Texas Austin, Dept Geog & Environm, Austin, TX 78712 USA' in json format, including Latitude, Longitude, UniversityName, City, Country."},
        {"role": "assistant", "content": f"{example}"}
    ]
    model = "gpt-3.5-turbo"

    for inst in institutes:
        # use chat-gpt
        prompt = f"Please get the information of '{inst}' in json format, including Latitude, Longitude, Name, City, Country. Please strictly follow the format of the example."
        inst_message = messages.copy()
        inst_message.append(
            {"role": "user", "content": prompt}
        )
        response = openai.ChatCompletion.create(
            model=model,
            messages=inst_message
        )
        print(response.choices[0].message.content)

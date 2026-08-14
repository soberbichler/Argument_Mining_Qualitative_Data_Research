from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from tqdm import tqdm
from together import Together
import numpy as np
from anthropic import Anthropic
import os
from openai import OpenAI
import pandas as pd
import re
from utils import *
import keys
import logging
import sys
import pickle
from time import sleep, strftime, localtime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_arguments():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    #dataset params
    parser.add_argument("-c", "--language_corpus",
                        dest="language_corpus",
                        default="english",
                        type=str,
                        choices=USER_PROMPT_LANG_STYLE.keys(),
                        help="""language to test""")

    parser.add_argument("-l", "--language_user",
                        dest="language_user",
                        default="english",
                        type=str,
                        choices=USER_PROMPT_LANG_STYLE.keys(),
                        help="""language to test""")

    parser.add_argument("-g", "--language_system",
                        dest="language_system",
                        default="english",
                        type=str,
                        choices=SYSTEM_PROMPT_LANG_STYLE.keys(),
                        help="""language to test""")

    parser.add_argument("-s", "--system_prompt_style",
                        dest="system_prompt_style",
                        type=str,
                        choices=SYSTEM_PROMPT_LANG_STYLE["english"].keys(),
                        default=None,
                        help="""System prompt to use""")

    parser.add_argument("-u", "--user_prompt_style",
                        dest="user_prompt_style",
                        type=str,
                        choices=USER_PROMPT_LANG_STYLE["english"].keys(),
                        help="""User prompt to use""")
    #models
    parser.add_argument("-m", "--model",
                        dest="model",
                        default=list(API_MODELS.keys())[0],
                        type=str,
                        choices=API_MODELS.keys(),
                        help="""Model to call""")

    parser.add_argument("-f", "--save_freq",
                        dest="save_freq",
                        type=int,
                        default=10,
                        help="""Save each # context.""")

    return parser.parse_args()

def read_dataset():

    #df = pd.read_csv("dataset_article-extraction-classification.csv")
    #df = pd.read_csv("OCR-correction.csv")
    df = pd.read_csv("OCR-correction_drive.csv")
    return df

def filter_dataset(df, lang):

    # Create a subset with only lang entries
    df_filtered = df[df['language'] == lang].reset_index(drop=True)

    return df_filtered


def estimate_input_tokens(prompt, lang_factor):
    return int(len(prompt) / lang_factor)  # average characters per token

def call_openai_api(context, api_model, lang_factor, user_prompt, system_prompt=None):


    prompt = f"{user_prompt} \\n\n{context}\n---\n"
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    max_tokens = api_model["max_tokens"] - estimate_input_tokens(prompt, lang_factor)
    if max_tokens <= 0:
        logger.info(f"ERROR - Prompt too big to process by model")
        return "ERROR - Prompt too big to process by model", None

    # Create a parameters dictionary
    params = {
        "model": api_model["entry_point"],
        "messages": messages,
        "temperature": PARAMETERS["temperature"],
        "top_p": PARAMETERS["top_p"],
        "seed": PARAMETERS["seed"],
        "logprobs": True,
        "max_tokens": max_tokens
    }

    retry_flag = False
    while not retry_flag:
        try:
            client_openai = OpenAI(api_key=keys.KEYS[api_model["provider"]])
            response = client_openai.chat.completions.create(**params)
            retry_flag = True
        except Exception as e:
            print(f"Fehler beim Aufruf der openAI-API: {e}")
            print("Reducing tokens by 100")
            params["max_tokens"] = params["max_tokens"] - 100
            sleep(1)

    content =  response.choices[0].message.content
    tokens_probabilities = [(x.token, x.logprob, np.exp(x.logprob) * 100) for x in response.choices[0].logprobs.content]

    return content, tokens_probabilities

API_MODELS["ChatGPT"]["function"] = call_openai_api

def call_togetherai_api(context, api_model, lang_factor, user_prompt, system_prompt=None):

    prompt = f"{user_prompt} \\n\n{context}\n---\n"
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    max_tokens = api_model["max_tokens"] - estimate_input_tokens(prompt, lang_factor)
    if max_tokens <= 0:
        logger.info(f"ERROR - Prompt too big to process by model")
        return "ERROR - Prompt too big to process by model", None

    # https://github.com/togethercomputer/together-python/blob/main/src/together/resources/chat/completions.py#L16
    params = {
        "model": api_model["entry_point"],
        "messages": messages,
        "temperature": PARAMETERS["temperature"],
        "top_p": PARAMETERS["top_p"],
        "max_tokens": max_tokens,
        "logprobs": 1,
        "stream": False,
        "seed": PARAMETERS["seed"]
    }

    retry_flag = False
    while not retry_flag:
        try:
            client_together = Together(api_key=keys.KEYS[api_model["provider"]])
            response = client_together.chat.completions.create(**params)
            retry_flag = True
        except Exception as e:
            print(f"Fehler beim Aufruf der togetherAI-API: {e}, retrying...")
            if "code: 429" in e._message:
                print("waiting...")
                sleep(1)
            elif "code: 422" in e._message:
                match = re.search(r'must be <= (\d+)\. Given: (\d+) `inputs` tokens and (\d+) `max_new_tokens`', e._message)
                if match:
                    limit = int(match.group(1))
                    inputs = int(match.group(2))
                    if inputs > limit:
                        logger.info(f"ERROR - Prompt (context)too big to process by model")
                        return "ERROR - Prompt (model) too big to process by model", None
                print("Reducing tokens by 100")
                params["max_tokens"] = params["max_tokens"] - 100

            sleep(1)

    content =  response.choices[0].message.content
    tokens_probabilities = [(x[0], x[1], np.round(np.exp(x[1]) * 100, 5)) for x in zip(response.choices[0].logprobs.tokens, response.choices[0].logprobs.token_logprobs)]

    return content, tokens_probabilities

API_MODELS["Llama3"]["function"] = call_togetherai_api
API_MODELS["Qwen"]["function"] = call_togetherai_api
API_MODELS["Nemotron"]["function"] = call_togetherai_api

def call_claude_api(context, api_model, lang_factor, user_prompt, system_prompt=None):

    prompt = f"{user_prompt}\n\n{context}\n---\n"
    messages = [{"role": "user", "content": prompt}]

    max_tokens = api_model["max_tokens"] - estimate_input_tokens(prompt, lang_factor)
    if max_tokens <= 0:
        logger.info(f"ERROR - Prompt too big to process by model")
        return "ERROR - Prompt too big to process by model", None

    params = {
        "model": api_model["entry_point"],
        "messages": messages,
        "temperature": PARAMETERS["temperature"],
        "top_p": PARAMETERS["top_p"],
        #"seed": PARAMETERS["seed"],
        #"logprobs": True,
        "max_tokens": max_tokens
    }

    if system_prompt:
        params["system"] = system_prompt

    retry_flag = False
    while not retry_flag:
        try:
            client = Anthropic(api_key=keys.KEYS[api_model["provider"]])
            response = client.messages.create(**params)
            retry_flag = True
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            print("Reducing tokens by 100")
            params["max_tokens"] = params["max_tokens"] - 100
            sleep(1)

    return response.content[0].text, None


API_MODELS["Claude"]["function"] = call_claude_api

def call_deepseek_api(context, api_model, lang_factor, user_prompt, system_prompt=None):
    """
    Calls the DeepSeek API to generate a response based on the provided text and prompts.

    Args:
        text (str): The input text to be processed.
        user_prompt (str): The user's prompt or instruction.
        model (str): The model to use for the API call.
        system_prompt (Optional[str]): An optional system-level prompt.
        temperature (float): Sampling temperature.
        top_p (float): Nucleus sampling parameter.
        top_k (Optional[int]): Top-k sampling parameter.
        max_tokens (int): Maximum number of tokens to generate.

    Returns:
        Optional[str]: The generated response with reasoning in <think> tags, or None if an error occurs.
    """
    # Format the prompt to explicitly request reasoning
    prompt = (
        f"Analyze the following and provide your reasoning in <think> tags, "
        f"followed by your response:\n\n"
        f"User Request: {user_prompt}\n"
        f"Text: {context}\n---\n"
    )
    messages = []

    # Add system prompt if provided
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Add user prompt
    messages.append({"role": "user", "content": prompt})

    max_tokens = api_model["max_tokens"] - estimate_input_tokens(prompt, lang_factor)
    if max_tokens <= 0:
        logger.info(f"ERROR - Prompt too big to process by model")
        return "ERROR - Prompt too big to process by model", None

    # Create a parameters dictionary
    params = {
        "model": api_model["entry_point"],
        "messages": messages,
        "temperature": PARAMETERS["temperature"],
        "top_p": PARAMETERS["top_p"],
        "seed": PARAMETERS["seed"],
        "logprobs": True,
        "max_tokens": max_tokens
    }

    retry_flag = False
    while not retry_flag:
        try:
            client = OpenAI(api_key=keys.KEYS[api_model["provider"]], base_url="https://api.deepseek.com")
            response = client.chat.completions.create(**params)
            retry_flag = True
        except Exception as e:
            print(f"Error calling the DeepSeek API: {e}")
            print("Reducing tokens by 100")
            params["max_tokens"] = params["max_tokens"] - 100
            sleep(1)

    content =  response.choices[0].message.content
    tokens_probabilities = [(x.token, x.logprob, np.exp(x.logprob) * 100) for x in response.choices[0].logprobs.content]

    return content, tokens_probabilities

API_MODELS["DeepSeek"]["function"] = call_deepseek_api


def main():
    args = parse_arguments()


    if not os.path.exists('./outs'):
        os.makedirs('./outs', mode=0o777)
    out_file = "{}-{}-{}-{}-{}-{}-{}.out".format(args.language_corpus, args.model, args.language_system, args.system_prompt_style,  args.language_user, args.user_prompt_style, strftime("%Y-%m-%d_%H:%M:%S", localtime()))

    file_handler = logging.FileHandler("%s/%s" % ('./outs', out_file.replace("out", "log")) )
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    df = read_dataset()
    df_filtered = filter_dataset(df, args.language_corpus)

    api_model = API_MODELS[args.model]
    model_function = API_MODELS[args.model]["function"]
    user_prompt = USER_PROMPT_LANG_STYLE[args.language_user][args.user_prompt_style]
    if args.system_prompt_style:
        system_prompt = SYSTEM_PROMPT_LANG_STYLE[args.language_system][args.system_prompt_style]
    else:
        system_prompt = None
    lang_factor = 3

    counter = 1
    outputs = []
    #df_filtered = df_filtered[108:]
    for index, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):

        #context = row["context_window"]
        context = row["context_window_ocr_ground-truth"]

        logger.info(row["Id"])
        content, tokens_probabilities = model_function(context, api_model, lang_factor, user_prompt, system_prompt)  # call specific model function

        output = {
            "Id": f"{index}_{row['Id']}",
            "content": content,
            "tokens_probabilities": tokens_probabilities
        }

        outputs.append(output)
        if counter % args.save_freq == 0:
            with open("%s/%s" % ('./outs', out_file), "wb") as ap:
                pickle.dump(outputs, ap)
        counter += 1
        sleep(0.1)


    with open("%s/%s" % ('./outs', out_file), "wb") as ap:
        pickle.dump(outputs, ap)

if __name__ == '__main__':
    """
    Starts the whole app from the command line
    """

    main()


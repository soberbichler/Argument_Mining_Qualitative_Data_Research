# Disable tokenizers parallelism warning
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_ENDPOINT'] = 'http://10.81.2.171:8090'

# Import libraries
import torch
import pandas as pd
import numpy as np
import random
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm.auto import tqdm

# Set random seeds for reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)

# Load CSV file
csv_filename = 'avanti_dataset_articles_split (1)_split.csv'
austrian_dataset_articles = pd.read_csv(csv_filename)
#austrian_dataset_articles = austrian_dataset_articles[:]

# Filter valid articles
df_valid = austrian_dataset_articles[austrian_dataset_articles['article_text'].notna()].copy()

# Load model
MODEL_ID = "oberbics/llama-3.1-8B-newspaper_argument_mining"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

# Add Llama 3.1 chat template if missing
if tokenizer.chat_template is None:
    tokenizer.chat_template = "{% if messages[0]['role'] == 'system' %}{% set loop_messages = messages[1:] %}{% set system_message = messages[0]['content'] %}{% else %}{% set loop_messages = messages %}{% set system_message = false %}{% endif %}{% for message in loop_messages %}{% if loop.index0 == 0 and system_message %}<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{{ system_message }}<|eot_id|>{% endif %}<|start_header_id|>{{ message['role'] }}<|end_header_id|>\n\n{{ message['content'] }}<|eot_id|>{% if loop.last and message['role'] != 'assistant' %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}{% endfor %}"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# System prompt
SYSTEM_PROMPT = '''You are an expert at analyzing historical texts and you hate to summarize

OUTPUT FORMAT - EXACTLY these 4 XML tags and NOTHING else:
<argument>Original argument text OR "NA"</argument>
<claim>Core claim (implication) in one sentence OR "NA"</claim>
<explanation>Why this is an argument OR "NA"</explanation>
<human_verification_needed>True OR False</human_verification_needed>

<argument>It is reported from Malta that the British war-ships "Exmouth," "Euryalus," "Minerva," and "Sutlej" have left for Messina. The French Government has sent two armoured ships and three destroyers to Messina. President Fallieres, Premier Clemenceau, Minister Pichon, and the Presidents of the Senate and Chamber have all sent messages of sympathy to the Italian Government. The help already proffered and accepted is insufficient for the purpose. There is pressing need of extraordinary measures of help, and provisions are in great demand. There is need of doctors, tents, clothing, and provisions for the survivors, who, deprived of all necessities, are exposed to the inclemencies of the winter weather. There is need of fire engines to cope with the flames that are raging among the ruins. The railway station has collapsed. Railway carriages have been destroyed. Almost all the railway employees are dead. The streets are no longer recognisable; they look like enormous fissures in a distant and extensive heap of ruins.</argument>
<claim>Current relief efforts are inadequate and much more extensive aid is urgently needed.</claim>
<explanation>The prefect explicitly argues that existing help is "insufficient" and makes a direct claim that "extraordinary measures" are needed, presenting a clear premise-conclusion structure about the inadequacy of current response.</explanation>
<human_verification_needed>False</human_verification_needed>

EXAMPLE WITHOUT ARGUMENT:
<argument>NA</argument>
<claim>NA</claim>
<explanation>NA</explanation>
<human_verification_needed>FALSE</human_verification_needed>

RULES:
- NEVER print the examples from the prompt or training
- Only output arguments that appear verbatim (or nearly verbatim) in the text
- NO SUMMARY; ONLY EXACT EXTRACTOM FROM THE TEXT; don't extract anything that is not in the text. Only extract word by word
- ONLY output these 4 XML tags
- Extract only original text without changes or use NA when you did not find an argument
- Factual reportings such as "Dem Vulkanausbruch folgten drei Sturzwellen in etwa 10 Meter Höhe" or "Almost all the inhabitants were killed; only a few thousands escaped death" are NO Arguments
- The CLAIM should say what the (implicite) argument implies, what the main conclusion is
- Give attention to implicit argumetns
- Only use human_verification_needed TRUE when highly uncertain
- If no argument exists, use NA for ALL fields without explanation except <human_verification_needed>FALSE or TRUE</human_verification_needed>
- More than one argument possible for one aticle, one unit has one clear clame and all the xml structures

VERIFICATION: BEfore you print the results, double check claims and explanations of the argument. When the claim is just a translation or the explanation states that this is not an argument, dont print it'''

# Extraction function
def extract_arguments(text, temperature=0.05):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract argumentative units from historical text in their original form, no summary.\n{text}"}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=5048).to(model.device)
    input_length = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=4000,
            temperature=temperature,
            top_p=0.95,
            repetition_penalty=1.15,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_tokens = outputs[0][input_length:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return response

# Processing function
def process_article(text):
    try:
        result = extract_arguments(str(text))
        return result
    except Exception as e:
        return f"ERROR: {str(e)}"

# Process articles
tqdm.pandas(desc="Processing")
df_valid['arguments'] = df_valid['article_split'].progress_apply(process_article)

# Merge results back to original dataframe
austrian_dataset_articles['arguments'] = "SKIPPED: NaN article_text"
austrian_dataset_articles.loc[df_valid.index, 'arguments'] = df_valid['arguments']

# Save results - both files contain ALL articles
austrian_dataset_articles.to_excel('avanti_dataset_with_arguments.xlsx', index=False)
austrian_dataset_articles.to_csv('avanti_dataset_with_arguments.csv', index=False)

# Argument Mining Pipeline and Graph-RAG

A research pipeline for applying **Large Language Models (LLMs) to argument mining in historical qualitative data**, including article extraction, supervised fine-tuning, reinforcement-learning post-training, evaluation, and knowledge-graph extraction.

The repository was developed around historical newspaper material related to the **1908 Messina earthquake** and explores how LLMs can identify argumentative passages in noisy historical text while preserving the original wording of the source.

## Overview

The pipeline covers several stages of LLM-assisted qualitative research:

1. **Article extraction** from historical newspaper/OCR data using multiple LLM providers.
2. **Evaluation of article extraction** against manually curated ground truth.
3. **Argument mining** to identify explicit and implicit argumentative units.
4. **Supervised fine-tuning** of Llama 3.1 using LoRA/PEFT.
5. **GRPO reinforcement-learning post-training** using task-specific reward functions.
6. **Knowledge-graph extraction** from identified arguments using a constrained ontology.

The argument-mining task produces structured annotations containing:

```xml
<argument>...</argument>
<claim>...</claim>
<explanation>...</explanation>
<human_verification_needed>True/False</human_verification_needed>
```

A central principle of the pipeline is to distinguish **argumentative language from factual reporting**. Extracted arguments retain the wording of the historical source, while the `claim` and `explanation` fields capture the interpretation of the argumentative function.

---

## Repository Structure

```text
Argument_Mining_Qualitative_Data_Research/
│
├── Annotation_Guidelines_Oberbichler_April_2026.pdf
│
├── README.md
│
├── Code Notebooks/
│   ├── AM_Fine_Tuning_Llama_HF_Job.ipynb
│   ├── Evaluation_code_article_extraction.ipynb
│   ├── GRPO_reinforcement-learning.ipynb
│   ├── Triplets_Fine_Tuning_Llama_HF_Job.ipynb
│   ├── article_extraction_utils_prompts_.py
│   └── article_extractor.py
│
└── Training Datasets/
    ├── argument_mining_training_dataset.xlsx
    ├── dataset_article-extraction-classification.csv.gz
    ├── post-training_multiarg_final.txt
    └── triplets_training_dataset.xlsx
```

---

## Pipeline

### 1. Article Extraction

`Code Notebooks/article_extractor.py`

The article-extraction component identifies relevant articles within larger OCR/context windows.

The current implementation supports configurable:

* corpus language;
* prompt language;
* system and user prompt variants;
* model/provider selection;
* periodic output saving.

The model configuration currently includes interfaces for:

* OpenAI models;
* Anthropic Claude;
* Together AI-hosted Llama models;
* Qwen;
* Nemotron;
* DeepSeek.

Prompt definitions and model configuration are contained in:

```text
Code Notebooks/article_extraction_utils_prompts_.py
```

The extraction prompts are tailored to historical newspaper material and, in this project, specifically to coverage of the Messina earthquake and its consequences.

---

### 2. Article-Extraction Evaluation

`Code Notebooks/Evaluation_code_article_extraction.ipynb`

This notebook evaluates LLM-extracted articles against manually curated ground truth.

It distinguishes outcomes including:

* True Positive;
* True Negative;
* False Positive;
* False Negative;
* under-extraction;
* over-extraction;
* content mismatch;
* formatting errors;
* cases requiring human verification.

Evaluation combines fuzzy text alignment and Levenshtein-based comparison with a task-specific success score.

This is particularly useful for historical OCR data, where minor spelling or OCR differences should not automatically be treated as failed extractions.

---

### 3. Supervised Argument-Mining Fine-Tuning

`Code Notebooks/AM_Fine_Tuning_Llama_HF_Job.ipynb`

This notebook prepares the annotated argument-mining dataset and performs adapter-based fine-tuning of:

```text
meta-llama/Llama-3.1-8B-Instruct
```

The training target consists of four structured fields:

```xml
<argument>Original argumentative passage</argument>
<claim>Underlying claim expressed or implied by the passage</claim>
<explanation>Explanation of why the passage is argumentative</explanation>
<human_verification_needed>False</human_verification_needed>
```

The notebook:

* cleans training data while preserving XML annotations;
* converts examples to Llama chat/instruction format;
* creates training and validation splits;
* uses PEFT/LoRA for parameter-efficient training;
* uses 4-bit quantization where appropriate;
* launches GPU training through Hugging Face Jobs;
* uploads the resulting adapter to the Hugging Face Hub;
* optionally merges the LoRA adapter back into the base model.

The checked-in supervised dataset is:

```text
Training Datasets/argument_mining_training_dataset.xlsx
```

The notebook expects training columns corresponding to:

```text
article_text
llm_training_answer
```

---

### 4. GRPO Reinforcement-Learning Post-Training

`Code Notebooks/GRPO_reinforcement-learning.ipynb`

This notebook explores **Group Relative Policy Optimization (GRPO)** as a second post-training stage after supervised fine-tuning.

Training is implemented using Hugging Face `trl` and task-specific reward functions.

Rather than rewarding only surface similarity, the reward system considers characteristics relevant to argument mining, including:

* correct identification of argumentative passages;
* false-positive and false-negative behavior;
* similarity to ground-truth arguments;
* duplicate/repeated arguments;
* claim quality;
* explanation quality;
* human-verification decisions;
* output-format compliance.

The associated post-training data is stored in:

```text
Training Datasets/post-training_multiarg_final.txt
```

Each training example contains source material, a ground-truth annotation, and synthetic outputs of different quality levels with associated reward values.

The goal is to encourage a model that not only reproduces the expected structure but also becomes more conservative about inventing arguments in passages that contain only factual reporting.

---

### 5. Knowledge-Graph / Triplet Extraction

`Code Notebooks/Triplets_Fine_Tuning_Llama_HF_Job.ipynb`

The final stage converts extracted arguments into structured knowledge-graph relations.

Arguments are mapped to constrained:

```text
subject → predicate → object
```

triples.

The notebook uses an explicitly defined ontology and rejects triples outside the permitted set, allowing qualitative interpretations to be transformed into a more standardized representation.

The training data is located at:

```text
Training Datasets/triplets_training_dataset.xlsx
```

Expected fields include:

```text
arguments
kg_subject
kg_predicate
kg_object
```

The notebook prepares instruction/response JSONL files and fine-tunes:

```text
meta-llama/Llama-3.1-8B
```

using LoRA.

---

## Annotation Guidelines

Detailed manual annotation instructions are provided in:

```text
Annotation_Guidelines_Oberbichler_April_2026.pdf
```

These guidelines should be consulted when:

* creating new ground-truth annotations;
* extending the training datasets;
* evaluating borderline argumentative passages;
* comparing human and model annotations.

Because argument identification—especially for implicit arguments—is interpretive, the pipeline includes a dedicated `human_verification_needed` field rather than assuming that every model prediction can be accepted automatically.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/soberbichler/Argument_Mining_Qualitative_Data_Research.git
cd Argument_Mining_Qualitative_Data_Research
```

Create a Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the main dependencies used across the notebooks:

```bash
pip install \
    pandas \
    openpyxl \
    scikit-learn \
    ftfy \
    numpy \
    torch \
    transformers \
    datasets \
    peft \
    accelerate \
    bitsandbytes \
    huggingface_hub \
    trl \
    sentencepiece \
    tqdm \
    openai \
    anthropic \
    together \
    fuzzywuzzy \
    python-Levenshtein
```

Individual notebooks also contain their own installation cells.

---

## Hugging Face Setup

The training notebooks are designed primarily for a **Google Colab + Hugging Face Jobs** workflow.

Authenticate with Hugging Face before launching training:

```bash
hf auth login
```

You will need:

* a Hugging Face account;
* a Hugging Face access token;
* access to the models used by the selected notebook;
* suitable GPU resources for model training.

Several training cells launch Hugging Face Jobs using an `a100-large` GPU environment.

When using Google Colab, the notebooks can also read `HF_TOKEN` from Colab Secrets.

**Do not commit API tokens or Hugging Face credentials to this repository.**

---

## Running the Notebooks

A typical workflow is:

```text
Historical OCR / newspaper data
          │
          ▼
   Article extraction
          │
          ▼
 Article-level evaluation
          │
          ▼
   Manual annotation
          │
          ▼
Supervised argument-mining
      fine-tuning
          │
          ▼
    GRPO post-training
          │
          ▼
Argument / Claim / Explanation
          │
          ▼
Knowledge-graph triplets
```

For argument-mining experiments, start with:

```text
Code Notebooks/AM_Fine_Tuning_Llama_HF_Job.ipynb
```

For reinforcement-learning experiments, continue with:

```text
Code Notebooks/GRPO_reinforcement-learning.ipynb
```

For structured ontology/triplet extraction, use:

```text
Code Notebooks/Triplets_Fine_Tuning_Llama_HF_Job.ipynb
```

---

## Important Reproducibility Notes

This repository contains **research code** rather than a packaged Python application. Some paths and filenames still reflect the original experiment/Colab environment and need to be adjusted before reproducing the experiments.

In particular:

### Dataset paths

`AM_Fine_Tuning_Llama_HF_Job.ipynb` currently refers to:

```text
/content/argument_mining_final.xlsx
```

while the repository contains:

```text
Training Datasets/argument_mining_training_dataset.xlsx
```

Likewise, the triplet notebook refers to:

```text
/content/training_2.xlsx
```

while the repository contains:

```text
Training Datasets/triplets_training_dataset.xlsx
```

Update these paths for your environment and verify the expected columns before running the notebooks.

### Article extractor

`article_extractor.py` currently contains:

```python
from utils import *
import keys
```

The repository instead provides:

```text
article_extraction_utils_prompts_.py
```

Before running the standalone extractor, either change the import accordingly or rename/copy the utility module to `utils.py`.

The script also expects a local API-key configuration and currently reads an experiment-specific dataset named:

```text
OCR-correction_drive.csv
```

These should be adapted to your environment and data source.

API credentials should preferably be supplied through environment variables or another secure secret-management mechanism rather than committed source files.

---

## Example Argument-Mining Output

Given a historical article containing an argumentative passage, the expected output has the following form:

```xml
<argument>
Exact passage copied from the historical source.
</argument>

<claim>
The central proposition or implication expressed by the passage.
</claim>

<explanation>
Why the passage should be interpreted as an argument rather than factual reporting.
</explanation>

<human_verification_needed>
False
</human_verification_needed>
```

If no argumentative unit is present, the corresponding fields can be represented as `NA`, depending on the training/evaluation stage.

Multiple arguments may be extracted from a single article.

---

## Research Motivation

Traditional qualitative analysis of historical sources is expensive to scale because identifying arguments requires more than keyword matching or topic classification.

Historical newspaper material introduces additional challenges:

* OCR errors;
* historical spelling;
* multilingual sources;
* implicit arguments;
* long and irregular article boundaries;
* mixtures of factual reporting and opinion;
* uncertainty requiring human interpretation.

This repository investigates how LLMs can assist with these tasks without removing the researcher from the analytical process.

The intended role of the models is therefore **research assistance rather than fully autonomous interpretation**.

---

## Extending the Project

Possible extensions include:

* adding new historical corpora;
* adapting the annotation scheme to other qualitative domains;
* comparing additional open and closed LLMs;
* evaluating inter-annotator agreement;
* developing dedicated argument-mining evaluation metrics;
* testing alternative reinforcement-learning reward functions;
* extending the knowledge-graph ontology;
* packaging the pipeline into reproducible command-line tools;
* replacing experiment-specific paths with configuration files;
* adding a unified `requirements.txt` or environment specification.

---

## Data and Responsible Use

The datasets are designed for research on historical qualitative material.

Researchers applying the pipeline to other collections should consider:

* copyright and licensing of source material;
* privacy when working with non-historical or sensitive documents;
* biases introduced by OCR and archival selection;
* model hallucination and false-positive arguments;
* uncertainty in interpreting implicit claims;
* the need for human validation of consequential interpretations.

Model-generated annotations should not automatically be treated as ground truth.

---

## License

No explicit software license is currently included in this repository.

If you intend to reuse or redistribute the code or datasets, please contact the repository owner or wait for an explicit license to be added.

---

## Contributing

Contributions, bug reports, and suggestions for improving the pipeline, annotation framework, evaluation methodology, or reproducibility are welcome through GitHub Issues and Pull Requests.


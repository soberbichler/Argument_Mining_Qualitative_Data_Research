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

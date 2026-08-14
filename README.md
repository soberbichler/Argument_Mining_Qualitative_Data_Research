# Argument Mining Pipeline and Graph-RAG

A research pipeline for applying **Large Language Models (LLMs) to argument mining in historical qualitative data**, including article extraction, supervised fine-tuning, reinforcement-learning post-training, argument extraction, evaluation, and knowledge-graph triplet extraction.

The repository was developed around historical newspaper material related to the **1908 Messina earthquake** and explores how LLMs can identify argumentative passages in noisy historical text while preserving the original wording of the source.

The pipeline transforms historical newspaper text into structured argumentative units and subsequently into **subject–predicate–object knowledge-graph triples**, providing graph-structured research data that can be used in downstream **Graph-RAG and knowledge-graph-based analysis workflows**.

## Overview

The pipeline covers several stages of LLM-assisted qualitative research:

1. **Article extraction** from historical newspaper/OCR data using multiple LLM providers.
2. **Evaluation of article extraction** against manually curated ground truth.
3. **Argument mining** to identify explicit and implicit argumentative units.
4. **Supervised fine-tuning** of Llama 3.1 using LoRA/PEFT for argument mining.
5. **GRPO reinforcement-learning post-training** using task-specific reward functions.
6. **Argument extraction at inference time** using the fine-tuned argument-mining model.
7. **Supervised fine-tuning for knowledge-graph extraction** from argumentative units.
8. **Triplet extraction** that maps arguments to structured `subject → predicate → object` relations.
9. **Ontology validation and expansion**, including confidence scores and identification of newly suggested triples.
10. **Evaluation datasets and combined argument–triplet results** for assessing the complete pipeline and supporting downstream graph-based analysis and Graph-RAG applications.

## Repository Structure

```text
Argument_Mining_Qualitative_Data_Research/
│
├── Annotation_Guidelines_Oberbichler_April_2026.pdf
├── README.md
├── arguments_triplets_results_all.xlsx
│
├── Code Notebooks/
│   ├── AM_Fine_Tuning_Llama_HF_Job.ipynb
│   ├── Evaluation_code_article_extraction.ipynb
│   ├── GRPO_reinforcement-learning.ipynb
│   ├── Triplets_Fine_Tuning_Llama_HF_Job.ipynb
│   ├── arguments_extractor.py
│   ├── triplets_extractor.py
│   ├── article_extraction_utils_prompts_.py
│   └── article_extractor.py
│
├── Training Datasets/
│   ├── argument_mining_training_dataset.xlsx
│   ├── post-training_multiarg_final.txt
│   └── triplets_training_dataset.xlsx
│
└── Evaluation Datasets/
    ├── dataset_article-extraction-classification.csv.gz
    └── triplets_evaluation_dadaset.xlsx
```

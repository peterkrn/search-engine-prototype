# -*- coding: utf-8 -*-
"""Copy of TF_IDF_InformationRetrieval.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vKw-A9eySHc7JI1teC6Etb_xtMLxeWr6
"""

import json
import concurrent.futures
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import math
from nltk.collections import Counter

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")


def intialize():
    data_dict_file = "data_dict.json"

    if os.path.exists(data_dict_file):
        # Load data_dict from the file
        with open(data_dict_file, "r", encoding="utf-8") as file:
            data_dict = json.load(file)
    else:
        # Run the code to initialize data_dict
        root_folder_path = "datasets"  # Update to your actual folder path
        data_dict = {}

        for folder_path, _, file_names in os.walk(root_folder_path):
            for file_name in file_names:
                if file_name.endswith(".txt"):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        data_dict[file_name] = content

        # Save data_dict to the file
        with open(data_dict_file, "w", encoding="utf-8") as file:
            json.dump(data_dict, file)

    return data_dict


def pos_tagger(nltk_tag):
    if nltk_tag.startswith("J"):
        return wordnet.ADJ
    elif nltk_tag.startswith("V"):
        return wordnet.VERB
    elif nltk_tag.startswith("N"):
        return wordnet.NOUN
    elif nltk_tag.startswith("R"):
        return wordnet.ADV
    else:
        return None


# Define a function for data cleaning
def preprocess_text(text):
    # Remove line breaks and extra whitespaces
    text = re.sub(r"\s+", " ", text).strip()

    # Handle commas in numbers
    text = re.sub(r"\$([0-9,]+)", lambda match: match.group(1).replace(",", ""), text)

    # Replace matched punctuation with an empty string
    text = re.sub(r"[^\w\s]", "", text)

    # Lowercasing
    text = text.lower()

    # Tokenize the text (using a word tokenizer)
    tokens = word_tokenize(text)

    # Removing common English stop words
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatizer
    lemmatizer = WordNetLemmatizer()
    pos_tagged = nltk.pos_tag(tokens)
    wordnet_tagged = list(map(lambda x: (x[0], pos_tagger(x[1])), pos_tagged))
    lemmatized_tokens = []
    for word, tag in wordnet_tagged:
        if tag is None:
            # if there is no available tag, append the token as is
            lemmatized_tokens.append(word)
        else:
            lemmatized_tokens.append(lemmatizer.lemmatize(word, tag))

    # Reassemble the text
    cleaned_text = " ".join(["".join(sentence) for sentence in lemmatized_tokens])

    return cleaned_text


"""# Count Term Frequency of Query for each documents"""


def tf(cleaned_data_dict):
    tf_file = "tf.json"

    if os.path.exists(tf_file):
        # Load tf from the file
        with open(tf_file, "r", encoding="utf-8") as file:
            tf = json.load(file)
    else:
        # Compute tf
        with concurrent.futures.ProcessPoolExecutor() as executor:
            tf_futures = {
                key: executor.submit(Counter, value.split())
                for key, value in cleaned_data_dict.items()
            }
        tf = {key: future.result() for key, future in tf_futures.items()}

        # Save tf to the file
        with open(tf_file, "w", encoding="utf-8") as file:
            json.dump(tf, file)

    return tf


"""# Count Inverse Document Frequency for document collection"""


def idf(cleaned_data_dict, tf):
    idf_file = "idf.json"

    if os.path.exists(idf_file):
        # Load idf from the file
        with open(idf_file, "r", encoding="utf-8") as file:
            idf = json.load(file)
    else:
        # Compute idf
        idf = {}
        total_docs = len(cleaned_data_dict)

        for doc_count in tf.values():
            for key, value in doc_count.items():
                idf[key] = idf.get(key, 0) + 1

        for key, value in idf.items():
            idf[key] = math.log(total_docs / (1 + value))

        # Save idf to the file
        with open(idf_file, "w", encoding="utf-8") as file:
            json.dump(idf, file)

    return idf


"""# Calculate TF-IDF Weights on each document"""


def tfidf(cleaned_data_dict, tf, idf):
    tfidf_file = "tfidf.json"

    if os.path.exists(tfidf_file):
        # Load tfidf from the file
        with open(tfidf_file, "r", encoding="utf-8") as file:
            tfidf = json.load(file)
    else:
        # Compute tfidf
        tfidf = {}

        for i in cleaned_data_dict.keys():
            tfidf_doc = {}
            for term, freq in tf[i].items():
                tfidf_doc[term] = freq * idf.get(term, 0)
            tfidf[i] = tfidf_doc

        # Save tfidf to the file
        with open(tfidf_file, "w", encoding="utf-8") as file:
            json.dump(tfidf, file)

    return tfidf


# TF-IDF Weight untuk query
def query_tfidf(preprocessed_query, idf):
    tfidf_query = {}
    for term in preprocessed_query:
        tfidf_query[term] = preprocessed_query.count(term) * idf.get(
            term, 0
        )  # tf-weight . idf-weight

    return tfidf_query


def cosine_similarity(query, doc):
    dot_product = sum((query[term] * doc[term]) for term in query if term in doc)
    magnitude_query = math.sqrt(sum((query[term] ** 2) for term in query))
    magnitude_doc = math.sqrt(sum((doc[term] ** 2) for term in doc))

    if magnitude_query == 0 or magnitude_doc == 0:
        return 0  # Avoid division by zero

    return dot_product / (magnitude_query * magnitude_doc)


def load_or_compute_cleaned_data(data_dict):
    cleaned_data_dict_file = "cleaned_data_dict.json"

    if os.path.exists(cleaned_data_dict_file):
        # Load cleaned_data_dict from the file
        with open(cleaned_data_dict_file, "r", encoding="utf-8") as file:
            cleaned_data_dict = json.load(file)
    else:
        # Compute cleaned_data_dict
        cleaned_data_dict = {
            key: preprocess_text(value) for key, value in data_dict.items()
        }

        # Save cleaned_data_dict to the file
        with open(cleaned_data_dict_file, "w", encoding="utf-8") as file:
            json.dump(cleaned_data_dict, file)

    return cleaned_data_dict


def search(keyword):
    data_dict = intialize()

    # Apply the preprocess_text function to each document content in the dictionary
    cleaned_data_dict = load_or_compute_cleaned_data(data_dict)

    tf_result = tf(cleaned_data_dict)

    idf_result = idf(cleaned_data_dict, tf_result)

    tfidf_result = tfidf(cleaned_data_dict, tf_result, idf_result)

    query = keyword
    preprocessed_query = preprocess_text(query)
    preprocessed_query = preprocessed_query.split()

    tfidfquery = query_tfidf(preprocessed_query, idf_result)
    result = sort_similarity(tfidfquery, data_dict, tfidf_result)
    return result


# Kalkulasi similarity tertinggi
def sort_similarity(tfidf_query, data_dict, tfidf):
    similarity_list = {}
    for key, value in tfidf.items():
        similarity = cosine_similarity(tfidf_query, value)
        if similarity > 0.1:
            similarity_list[key] = similarity
    sorted_similarity_list = dict(
        sorted(similarity_list.items(), key=lambda item: item[1], reverse=True)
    )

    result_list = [
        (key, value, data_dict[key]) for key, value in sorted_similarity_list.items()
    ]

    return result_list

""" Tags sentences for topics in a provided tag list.
    Matches tagged sentences to corresponding review with the same key number
    Josh Phillips, RAC co-op, Spring 2021 """

import copy
import pandas as pd
import itertools
from tqdm import tqdm

import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm

nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('wordnet')

sid = SentimentIntensityAnalyzer()



def get_stop_words():
    # importing stop words for lemma function
    stop_words = set(stopwords.words("english"))

    # remove these words from the default stopwords list because they are important to the meaning of a review
    negation = ["mustn't", "aren't", 'ain', 'mightn', 'needn', 'wasn', "shan't",
                'hadn', "mightn't", "isn't", 'hasn', 'shan', "hadn't", 'shouldn', "needn't",
                'doesn', 'haven', 'no', "wasn't", 'mustn', "haven't", 'didn', "weren't",
                "wouldn't", "don't", "couldn't", 'weren', 'nor', 'aren', "didn't", 'wouldn',
                'isn', "hasn't", 'couldn', 'don', "doesn't", "won't", 'off', 'on', "shouldn't", 'not',
                'does', 'did']
    for word in negation:
        stop_words.remove(word)

    # add these words into our stop word list because there are so many promoted reviews and we'll
    # search fot those separately
    promoted = ['review', 'collected', 'part', 'promotion', 'rating', 'provided', 'verified',
                'purchaser']
    for word in promoted:
        stop_words.add(word)
    
    return stop_words
    
def lemmatise(sentence, stop_words):
    """
    input: sentence, any stop words to remove from the sentence
    output: lemmatised version of the sentence
    """
    words = nltk.word_tokenize(sentence)
    # Remove punctuations and make lowercase
    words = [word.replace("'", "") for word in words]
    words = [word.lower() for word in words if word.isalpha()]
    # Lemmatisation
    lem = WordNetLemmatizer()
    words = [lem.lemmatize(word) for word in words if not (word in stop_words)]  # lem word if word not in stop_words
    lemma = " ".join(words)
    return lemma



def excelSheetToDf(file_name, sheet_name):
    """
    input: string fileName: name of excel file ending in .xlsx
           string sheetName: name of the sheet you want to pull from fileName
    output: pandas dataframe df: uses the first row in the excel file as headers
    """
    excel_file = pd.ExcelFile(file_name)
    df = excel_file.parse(sheet_name)
    return df


def permutationsOfTags(list_of_tag_identifiers):
    """
    input: Tag list .xlsx file
    output: a list containing all the permutations of the keywords composing the tag list
    """
    all_permutations = []
    for item in list_of_tag_identifiers:
        item = item.split(" ")
        perms = list(itertools.permutations(item))
        for permutation in perms:
            permutation = list(permutation)
            phrase = " ".join(permutation)
            all_permutations += [phrase]
    return redundantSearchEliminator(all_permutations)


def redundantSearchEliminator(search_terms):
    """
    input: List of all the search terms:
           -This can be the permutations of the tag list
           -Can also be a list of keywords from the tag list directly
    output: The list with the redundant searches eliminated
    """
    search_terms = list(sorted(search_terms, key=len))
    redundant_search_indexes = []
    for index1, current_item in enumerate(search_terms):
        for index2, next_items in enumerate(search_terms[index1 + 1:]):
            if " " + str(current_item) in " " + str(next_items):
                redundant_search_indexes += [index1 + index2 + 1]
    redundant_search_indexes = list(set(redundant_search_indexes))
    redundant_search_indexes = copy.deepcopy(list(sorted(redundant_search_indexes)))

    count = 0
    for item in reversed(redundant_search_indexes):
        search_terms.pop(int(item))
        count += 1
    return search_terms


def promotedTagger(data_frame):
    """ special tag that gets its own function because it searches the review to see if it was part of a promotion"""

    print("\nTagging for the Promoted Review tag.")
    print("Searching for the following phrases: ")
    print("'This review was collected as part of a promotion'")  # Promoted reviews must contain this sentence
    promoted_keys = []
    result = []
    for index, row in tqdm(data_frame.iterrows(), total=data_frame.shape[0]):
        row_tag = False
        if str("review was collected as part of a promotion") in str(row['review_text']).lower():
            row_tag = True
            promoted_keys += [row['Key']]  # Stores the Key of promoted reviews
        result += [row_tag]
    return {"Promoted Review Bool List": result, "Promoted Keys": promoted_keys}


def verifiedPurchase(data_frame):
    """ special tag that gets its own function because it searches the sentence
    and not the lemma """

    print("\nTagging for the THD Verified Purchase tag.")
    print("Searching for the following phrases: ")
    print("'Rating provided by a verified purchaser'")
    verified_purchase_keys = []
    result = []
    for index, row in tqdm(data_frame.iterrows(), total=data_frame.shape[0]):
        row_tag = False
        if str("Rating provided by a verified purchaser") in str(row['sentence']):
            row_tag = True
            verified_purchase_keys += [row['Key']]  # Stores the Key of verified purchases
        result += [row_tag]
    return [result, verified_purchase_keys]


def main(tag_file, reviews_df, sentences_df, output_file, tag_by_method='lemma'):

    # read in the tags from our tag list excel file
    tag_df = excelSheetToDf(tag_file, 'Tags')
    tags = []
    for column in tag_df.columns:
        tags += [[column, tag_df[column].tolist()]]

    # Load the sentence data frame
    #df = excelSheetToDf(previous_output, 'Sentences')
    df = sentences_df

    # now we are going to see if the reviews are part of a promotion
    promoted_tagger_dict = promotedTagger(reviews_df)
    reviews_df["Promoted Review"] = promoted_tagger_dict["Promoted Review Bool List"]
    
    sentences_df["Promoted Review"] = False
    
    # now lets tag all the sentences that originated from a promoted review
    for index, row in sentences_df.iterrows():
        if row["Key"] in promoted_tagger_dict["Promoted Keys"]:
            sentences_df.at[index, "Promoted Review"] = True
            
            
    
    verified_purchase_tags_and_keys = verifiedPurchase(df)
    df['THD Verified Purchaser'] = verified_purchase_tags_and_keys[0]

    ##########################################################################
    # for every tag in my tag list                                           #
    # 1) load the identifiers/keywords                                       #
    # 2) get the permutation or not                                          #
    # 3) eliminate the redundant searches                                    #
    # 4) traverse the dataframe and search the lemma for the keywords        #
    #    /identifiers                                                        #
    # 5) Store the key of the sentence so that we can easily flag the review #
    #    that the sentence originates from                                   #
    ##########################################################################
    
    
    if tag_by_method == "lemma":
        print("Tagging using the lemma method")
        # this way uses lemma
        keychain = []
        for tag in tags:
            print("\nTagging for the " + tag[0] + " tag.")
            print("Searching for the following phrases: ")
            result = []
            key_ring = []
            
            stop_words = get_stop_words()
            my_list_of_identifiers = [lemmatise(identifier.lower(), stop_words) for identifier in tag[1] if str(identifier) != 'nan' and str(identifier) != '']
            # remove empty string from my_list_of_identifiers
            my_list_of_identifiers = [identifier for identifier in my_list_of_identifiers if str(identifier) != '']
            print(my_list_of_identifiers)
            
            tag_identifiers = redundantSearchEliminator(my_list_of_identifiers)
            print(tag_identifiers)
            for index, row in tqdm(df.iterrows(), total=df.shape[0]):
                row_tag = False
                for tag_identifier in tag_identifiers:
                    if str(" ") + str(tag_identifier) in str(" ") + str(row['lemma']):
                        row_tag = True
                        key_ring += [row['Key']]
                        break
                result += [row_tag]
            df[tag[0]] = result
            keychain += [key_ring]
    
    elif tag_by_method == "sentence":
        print("Tagging using the sentence method")
        # this way uses sentence
        keychain = []
        for tag in tags:
            print("\nTagging for the " + tag[0] + " tag.")
            print("Searching for the following phrases: ")
            result = []
            key_ring = []
            
            my_list_of_identifiers = [identifier.lower() for identifier in tag[1] if str(identifier) != 'nan']
            # remove empty string from my_list_of_identifiers
            my_list_of_identifiers = [identifier for identifier in my_list_of_identifiers if str(identifier) != '']
            
            tag_identifiers = redundantSearchEliminator(my_list_of_identifiers)
            print(tag_identifiers)
            for index, row in tqdm(df.iterrows(), total=df.shape[0]):
                row_tag = False
                for tag_identifier in tag_identifiers:
                    if str(" ") + str(tag_identifier) in str(" ") + str(row['sentence']):
                        row_tag = True
                        key_ring += [row['Key']]
                        break
                result += [row_tag]
            df[tag[0]] = result
            keychain += [key_ring]
            
    else:
        print("tagging method not recognized by Tagger.py")
        input("Please pass in the correct arguments and restart the program.")
        return
    
    
    
    # Now we will use the key values in keychain to match the sentence tags to the reviews
    #reviews_data_frame = excelSheetToDf(previous_output, 'Reviews')
    reviews_data_frame = reviews_df
    

    reviews_data_frame['THD Verified Purchaser'] = False
    for key in set(verified_purchase_tags_and_keys[1]):
        reviews_data_frame.loc[reviews_data_frame.Key == key, 'THD Verified Purchaser'] = True

    print('Matching Sentences to Reviews')
    for index, current_key_ring in tqdm(enumerate(keychain), total=len(keychain)):
        reviews_data_frame[tags[index][0]] = False
        for key in current_key_ring:
            reviews_data_frame.loc[reviews_data_frame.Key == key, tags[index][0]] = True

    # output to excel file specified above
    print("Exporting to:", output_file)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sentences', index=False)
    reviews_data_frame.to_excel(writer, sheet_name='Reviews', index=False)
    writer._save()

    return reviews_data_frame, df


if __name__ == '__main__':
    
    tag_file = input("Enter name of tag file")
    reviews_file_name = input("Enter name of reviews df file")
    reviews_sheet_name = input("Enter name of reviews sheet")
    sentences_file_name = input("Enter name of sentences df file")
    sentences_sheet_name = input("Enter name of sentences sheet")
    
    output_file = input("Enter name of output file")
     
    main(tag_file, pd.read_excel(reviews_file_name, sheet_name=reviews_sheet_name), pd.read_excel(sentences_file_name, sheet_name=sentences_sheet_name), output_file)

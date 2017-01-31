import profile
import csv

# Here, we are reusing the document distance code
from docdist_dict import (get_words_from_string, count_frequency, vector_angle) #Imported from docdist_dict instead of docdist because docdist_dict had the same functions but with a slower run time

# As a convention, "constant" variable names are usually written in all-caps
OUTPUT_FILE = 'Sentence_database-hw3-nboesel.csv'

MASTER_FILE = 'Sentences_Table_MasterList.csv'
SENTENCE_DB_FILE = 'Sentence_Database_Without_ID.csv'
# MASTER_FILE = 'Sentences_Table_MasterList.csv'
# SENTENCE_DB_FILE = 'Sentence_Database_Without_ID.csv'

def main():
    global MASTER_FILE, SENTENCE_DB_FILE

    # we will be collecting each row of the output file in this list
    output = []
    row_count = 0

    # looping through the SENTENCE_DB_FILE to process each row
    for row in get_csv_rows(SENTENCE_DB_FILE): #
        set_sentence_id(row) #Giving each row a Sent_ID from the master file
        replace_target_with_blank(row) # Replace the target word with XXXXX

        if row['SentID_GM'] != 'NA': #If the row doesn't have a SentID ...
            lookup_similar_id(row) #Lookup and assign it a similar ID from a sentence that is similar
            find_alternate_sentence(row) #Find the sentence that is most similar to this sentence
            find_unique_targets(row) #This finds a new unique target word for this sentence that should be assigned to this sentence

        output.append(row) #Adds the row to the output list
        row_count += 1 #Makes a counter for ths row count
        print(row_count) #Prints the row count

        write_output_file(output) #Writes the output list into a csv file

def set_sentence_id(row):
    '''
        If you look at the SENTENCE_DB_FILE, each row has a Sentence with a missing SentID_GM
        SentID_GM can be found in the MASTER_FILE
        So, we use the MASTER_FILE data to find SentID_GM for each Sentence

        # -------------------------------------------------------------------------
        # Implement a better way to "lookup" SentID_GM,
        # without looping through each row again and again
        #
        # Ask yourself:
        # -------------
        #   - Is "list" the best data structure for "lookup / search"?
        #   - What is the 'type' of running time for the current implementation?
        #     Is it linear or quadratic?
        #
        # -------------------------------------------------------------------------

    '''
    #New code
    for record in get_csv_rows(MASTER_FILE):
        # record is a row in MASTER_FILE
        if record['Sentence_with_Target'].strip() == row['Sentence'].strip():
            # found a matching sentence!
            row['SentID_GM'] = record['SentID_GM']
            break

        else:
            # the default value
            row['SentID_GM'] = 'NA'

    #Old code
    # for record in get_csv_rows(MASTER_FILE): #Loops through the master file
    #     # record is a row in MASTER_FILE
    #     if record['Sentence_with_Target'].strip() == row['Sentence'].strip(): #If you find a sentence in the master file that is the same as a sentence in the saple file
    #         # found a matching sentence!
    #         row['SentID_GM'] = record['SentID_GM'] #Assign the Sentence ID to be equal to that of the one in the master file
    #         break
    #
    #     else:
    #         # the default value
    #         row['SentID_GM'] = 'NA' #If the sentence doesn't match any sentence in the master file, then assign the Sentence ID to be equal to NA


def replace_target_with_blank(row):
    '''
        Each row in SENTENCE_DB_FILE has a "Target" word like "[education]".
        In this function, we replace the target word with "XXXXX", and
        store its value in "Sentence_With_Blank" column

        # -------------------------------------------------------------------------
        # Implement a better way to replace the Target word with XXXXX,
        # without looping through the words
        #
        # Ask yourself:
        # -------------
        #   - Is there an inbuilt python function,
        #     that can be used to substitute a word with another word?
        #
        # -------------------------------------------------------------------------

    '''

    new_words = [] #Create an empty list

    # Here, we split the sentence into words and loop through it till we find the target
    for word in row['Sentence'].split(): #Loop through each word in the sentence
        if word[0]=='[' and (word[-1]==']' or word[-2:]=='].') and word[1:-1]==row['Targ']: #If the word starts and ends with brackets and is the same word as the target word
            new_words.append('XXXXX') #Add 'XXXXX' to the new_words list
        else:
            new_words.append(word) #If the word is different then the target word, just append the word to the new_words list

    row['Sentence_With_Blank'] = ' '.join(new_words) #The new row called Sentence_With_Blank will be equal to the same sentence, except the target word will be replaced with XXXXX


def lookup_similar_id(row):
    '''
        The MASTER_FILE also has a column 'SimilarTo_SentID_GM',
        which is the sentence ID of a similar sentence in the MASTER_FILE.

        In this function, we lookup the similar sentence for the given 'row',
        using the data in the MASTER_FILE

        # -------------------------------------------------------------------------
        # Implement a better way to find similar sentence,
        # without looping through the each row again and again
        #
        # Ask yourself:
        # -------------
        #   - Is "list" the best data structure for "lookup / search"?
        #   - What is the 'type' of running time for the current implementation?
        #     Is it linear or quadratic?
        #   - Can I reuse something from a previous step?
        #
        # -------------------------------------------------------------------------

    '''

    similar_to = None #Initialize similar_to variable
    # Here we get SimilarTo_SentID_GM for this row's SentID_GM using the MASTER_FILE
    for record in get_csv_rows(MASTER_FILE): #Looping through the rows of the master file
        # record is a row in MASTER_FILE
        if record['SentID_GM'] == row['SentID_GM']: #If the Sentence ID of the row is equal to the Sentence ID of the sample row
            # found a match
            similar_to = record['SimilarTo_SentID_GM'] #The variable similar_to gets set to the Sentence ID of a sentence it is similar to
            break

    # then we find the similar sentence from the MASTER_FILE
    if similar_to is not None: #If there the sentence has a nother similar sentence
        for record in get_csv_rows(MASTER_FILE): #Loop thorugh the master file
            # record is a row in MASTER_FILE
            if record['SentID_GM'] == similar_to: #When you find the similar sentence
                row['SimilarTo_Sentence'] = record['Sentence_with_Target'] #The row Similar_To_Sentence is created and is equal to that similar sentence
                row['SimilarTo_SentID_GM'] = similar_to #The row SimilarTo_SentID_GM is created and is equal the Sentence ID of that similar sentence
                break

def find_alternate_sentence(row):
    '''
        Just like SimilarTo_Sentence and SimilarTo_SentID_GM, we will determine
        Alternate_SimilarTo_Sentence and Alternate_SimilarTo_SentID_GM
        by calculating the cosine distance between two sentences
        using the **document distance** code that we discussed in the previous class

        # -------------------------------------------------------------------------
        # Your aim in this function is to speed up the code using a simple trick
        # and a modification
        #
        # ----------
        # PRE-BONUS hints (to help get to 10x speedup):
        # Hint #1: Look at the other files in the folder.
        # Hint #2: You can speed up this function A LOT without changing a
        #          single line of it!
        #
        # Ask yourself:
        # -------------
        #   - Why are the functions called here so slow?
        #   - Is there something you learned in the class about "document distance" problem,
        #     that can be used here?
        #
        # -----
        # BONUS hints: (to get more than 10x speedup --- only try this after you
        #               have gotten a 10x speedup by completing the above changes and
        #               optimizing the other functions in this file)
        #
        # Hint #1: Is there a step which can be taken out of the 'for' loop?
        #
        # Hint #2: This code calculates the cosine distance between the given row's Sentence
        # and the Sentence_with_Target all the rows in MASTER_FILE.
        # This is repeated for each 'row' in SENTENCE_DB_FILE.
        # In first iteration, you already calculate the cosine distance of
        # "I go to school because I want to get a good [education]."
        # and all the rows in the MASTER_FILE
        # and that includes "I go to school because I want to get a good [education]."
        # This is repeated in 2nd iteration for "I go to school because I want to get a good [education].".
        #
        # Can you cache (store) these calculations for future iterations?
        # What would be the best data structure for caching?
        # Try to further optimize the code using a cache
        # -------------------------------------------------------------------------

    '''

    # find alternate similar sentence using document distance
    similar_sentence = None #Initialize similar_sentnce variable
    d = {}
    for record in get_csv_rows(MASTER_FILE): #Loop through master file
        # record is a row in MASTER_FILE

        if record['SentID_GM'] == row['SentID_GM']:
            # ignore the same sentence
            continue

        # get frequency mapping for row['Sentence']
        row_word_list = get_words_from_string(row['Sentence']) #Puts the words in the sentence as strings in a list
        row_freq_mapping = count_frequency(row_word_list) #Gets the count for each word for how many times it appears in the Sentence in the form of a dictionary

        # get frequency mapping for record['Sentence_with_Target']
        record_word_list = get_words_from_string(record['Sentence_with_Target']) #Puts the words from the Sentence that has the target into string into a list
        record_freq_mapping = count_frequency(record_word_list) #Gets the count for each of these word for how many times it appears in the sentence in the form of a dictionary

        distance = vector_angle(row_freq_mapping, record_freq_mapping) #Inputs the two word counts of each sentence in the forms of dictionaries and then computes the angle between these sentences
        if 0 < distance < 0.75: #If the angle is between 0 and .75
            if (not similar_sentence) or (distance < similar_sentence['distance']):
                similar_sentence = {
                    'distance': distance,
                    'Sentence_with_Target': record['Sentence_with_Target'],
                    'SentID_GM': record['SentID_GM'] #Creates a dictionary of values for the new similar sentence, where the distance is set equal to the angle between the two setnences
                    #The Key Sentence_with_Target will be equal to the sentence from the master file and the Sentence ID will be the same as the Sentence ID in the master file
                }

    if similar_sentence and similar_sentence['SentID_GM'] != row.get('SimilarTo_SentID_GM'): #If this new similar sentence isn't equal to the old similar sentence
        row['Alternate_SimilarTo_SentID_GM']  = similar_sentence['SentID_GM'] #A new row is created called Alternate_SimilarTo_SentID_GM, which is equal to the Sentence ID generated in the dictionary above
        row['Alternate_SimilarTo_Sentence']  = similar_sentence['Sentence_with_Target'] #Another new row is created called Alternate_SimilarTo_Sentnce, which is equal to the sentence generated in the dictionary above

    # return(similar_sentence)

def find_unique_targets(row):
    '''
        This steps finds [target] word in "SimilarTo_Sentence" and "Alternate_SimilarTo_Sentence",
        selects only unique target word(s), and saves it in `row['SimilarTo_Targets']`

        # -------------------------------------------------------------------------
        # Implement a better way to find unique target words,
        # without looping through the words
        #
        # Ask yourself:
        # -------------
        #   - Can you use regular expressions to do this?
        #   - What is the data structure that stores only unique values?
        #     Can it be used here instead of checking "if target not in targets:"?
        #     Try searching the web for "python get unique values from a list".
        #
        # -------------------------------------------------------------------------

    '''

    # find unique targets from similar sentences
    targets = [] #Create empty list
    for key in ('SimilarTo_Sentence', 'Alternate_SimilarTo_Sentence'): #Loops through the two similar sentences for each sentence
        for word in row.get(key, '').split(): #Loops through words in each of these sentences
            if word.startswith('[') and word.endswith(']'): #If the word starts with a bracket and ends with a bracket
                target = word[1:-1] #The target word is equal to the word in between those brackets
                if target not in targets: #If the word isn't already in the list
                    targets += [target]  #Add the new target word

            elif word.startswith('[') and word.endswith('].'): #Also if the word starts with a bracket and ends with a bracket and a period
                target = word[1:-2] #Target is equal to the word in between those brackets
                if target not in targets: #If that word isn't already in the list
                    targets += [target] #Add the word to the list

    row['SimilarTo_Targets'] = ','.join(targets) #Create a new row called SimilarTo_Targets, which is equal to the target list just created


def get_csv_rows(filename):
    '''Read the CSV file using DictReader and then append all rows in a list'''
    with open(filename, 'r', newline='') as input_file: #Open the file and read it
        reader = csv.DictReader(input_file, delimiter=',', quotechar='"') #Creates a nested dictionary of lists equal to the rows of the CSV files
        #New code
        return list(reader) #Reads the daya from the dictionary reader into a list

        #Old code
        # data = [] #Create an empty list
        # for row in reader: #Loop through the dictioanry
        #     data.append(row) #Append the keys into the list
        #
        # return data #Return the list


def write_output_file(output):
    '''Write output into a new CSV file. Uses the OUTPUT_FILE variable to determine the filename.'''
    global OUTPUT_FILE
    with open(OUTPUT_FILE, 'w', newline='') as output_file_obj: #Create the output file
        sentence_db_writer = csv.DictWriter(output_file_obj,
                                fieldnames=["SentID_GM", "Sentence", "Targ", "Sentence_With_Blank",
                                        "SimilarTo_Sentence", "SimilarTo_SentID_GM",
                                        "Alternate_SimilarTo_Sentence", "Alternate_SimilarTo_SentID_GM",
                                        "SimilarTo_Targets"],
                                extrasaction="ignore", delimiter=",", quotechar='"') #Set the names of the rows

        sentence_db_writer.writeheader() #Write the names of the rows

        for row in output: #Loop through the ouput
            sentence_db_writer.writerow(row) #Write the data for each row


if __name__ == '__main__':
    profile.run('main()') #Run the function
    # main()

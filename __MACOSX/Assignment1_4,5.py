#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
from glob import glob
from pprint import pprint
from collections import defaultdict


# In[2]:


play_files = glob("play_files/*.txt")
play_files


# In[7]:


lines = []
for play_file in play_files:
    with open(play_file, "r") as fp:
        lines.append(fp.read().split("\n\n"))


# In[8]:


for line_list in lines:
    print(len(line_list))


# In[10]:


def get_start_line(play_lines):
    scene_1_line = -1
    start_line = -1
    line_counter = 0
    
    while start_line == -1:
        # Loop to search for line containing "SCENE I"
        # Will only be executed for the first iteration
        # of the parent while loop
        while scene_1_line == -1:
            line = play_lines[line_counter]
            if line.startswith("SCENE I\t"):
                scene_1_line = line_counter
            line_counter += 1
        
        # Search for the chunk for the first dialogue
        line = play_lines[line_counter]
        if line[0].isalpha():
            start_line = line_counter
            
        line_counter += 1
    
    return start_line


# ### Get the index of the chunk containing the first dialogue

# In[11]:


start_lines = [get_start_line(play_lines) for play_lines in lines]
start_lines


# In[ ]:


for line_num, play_lines in zip(start_lines, lines):
    pprint(play_lines[line_num])
    print("="*100)


# In[12]:


lines_with_starting_point = [
    play_lines[start_line_num:] for start_line_num, play_lines in zip(start_lines, lines)
]


# ### Verify the starting point by printing first few dialogues of each play

# In[13]:


for play_lines in lines_with_starting_point:
    pprint(("\n" + "<=>"*5 + "\n").join(play_lines[:2]))
    print("="*100)


# ### Remove chunks containing terms like ACT I, ACT II, SCENE I, SCENE II, etc

# In[14]:


def filter_act_and_scene_lines(play_lines):
    filtered_lines = []
    
    for line in play_lines:
        if line.startswith("ACT"):
            continue
        elif line.startswith("SCENE"):
            continue
        else:
            filtered_lines.append(line)
            
    return filtered_lines


# In[15]:


lines_without_act_and_scene_lines = [
    filter_act_and_scene_lines(play_lines) 
    for play_lines in lines_with_starting_point
]


# In[16]:


# Verify that the number of chunks have reduced after removal of ACT and SCENE chunks
for play_lines in lines_without_act_and_scene_lines:
    print(len(play_lines))


# ### Print lines not starting with alphabetical characters to see different cases

# In[18]:


for play_idx, play_lines in enumerate(lines_without_act_and_scene_lines):
    print(play_idx)
    for line in play_lines:
        if not line[0].isalpha():
            pprint(line)
            print("-"*25)
    print("="*500)


# In[20]:


def remove_text_with_square_brackets(play_lines):
    filtered_lines = []
    for line in play_lines:    
        if '[' in line and ']' in line:
            left_bracket_pos = line.find("[")
            right_bracket_pos = line.find("]")
            
            cleaned_line = line[:left_bracket_pos] + line[right_bracket_pos+1:]
            
            # Optionally print the 'before' and 'after' strings 
            # to test the correctnes of logic
            # print(line, "=>", cleaned_line)

            if cleaned_line.strip():
                filtered_lines.append(cleaned_line)
                
        else:
            filtered_lines.append(line)
                
    return filtered_lines


# In[21]:


lines_without_square_bracket_text = [
    remove_text_with_square_brackets(play_lines)
    for play_lines in lines_without_act_and_scene_lines
]


# ### Print the lines again after removing all text contained between square brackets

# In[22]:


for play_idx, play_lines in enumerate(lines_without_square_bracket_text):
    print(play_idx)
    for line in play_lines:
        if not line[0].isalpha():
            pprint(line)
            print("-"*25)
    print("="*500)


# In[23]:


def remove_play_name(play_lines):
    whitespace = {' ', '\t', '\n'}
    filtered_lines = []
    
    for line in play_lines:
        if line[0] in whitespace and line.strip().isupper():
            continue
        else:
            filtered_lines.append(line)
            
    return filtered_lines


# In[24]:


lines_without_play_name = [
    remove_play_name(play_lines)
    for play_lines in lines_without_square_bracket_text
]


# ### Print the lines again after removing names of the plays

# In[25]:


for play_idx, play_lines in enumerate(lines_without_play_name):
    print(play_idx)
    for line in play_lines:
        if not line[0].isalpha():
            pprint(line)
            print("-"*25)
    print("="*500)


# ### Handle special case for the play shakespeare-comedy-7.txt

# In[26]:


for line in lines_without_play_name[1]:
    if line.startswith("ANTIPHOLUS\t"):
        pprint(line)
        print("-"*25)


# In[27]:


lines_without_play_name[1] = [
    line for line in lines_without_play_name[1]
    if not line.startswith("ANTIPHOLUS\t")
]


# ### Verify that the special case lines have been removed

# In[28]:


for line in lines_without_play_name[1]:
    if line.startswith("ANTIPHOLUS\t"):
        pprint(line)
        print("-"*25)


# # Logic to parse dialogues

# In[29]:


character_dialogue_info_in_plays = {}

for play_idx, play_lines in enumerate(lines_without_play_name):
    character_dialogue_info_in_plays[play_idx] = {}
    char_name = None

    for line in play_lines:
        if line[0].isalpha():
            tab_pos = line.find('\t')
            char_name = " ".join(line[:tab_pos].split())
            char_words = line[tab_pos+1:].rstrip()
            
            # TODO: Use collections.defaultdict
            if char_name not in character_dialogue_info_in_plays[play_idx]:
                character_dialogue_info_in_plays[play_idx][char_name] = []
                character_dialogue_info_in_plays[play_idx][char_name].append(char_words)
            else:
                character_dialogue_info_in_plays[play_idx][char_name].append(char_words)
            
        else:
            # Printing separate chunks of dialogue with character names
            # to verify that we are these chunks with the correct
            # character
            print(char_name, "=>")
            pprint(line)
            character_dialogue_info_in_plays[play_idx][char_name].append(line.strip())


# ### Join list with chunks of dialogues in a single string for each character

# In[30]:


character_cleaned_dialogue_info_in_plays = {}

for play_idx in character_dialogue_info_in_plays:
    character_cleaned_dialogue_info_in_plays[play_idx] = {}
    for character in character_dialogue_info_in_plays[play_idx]:
        character_cleaned_dialogue_info_in_plays[play_idx][character] =             " ".join(character_dialogue_info_in_plays[play_idx][character])


# In[32]:


pprint(character_cleaned_dialogue_info_in_plays[0])


# ### Split text into token

# In[33]:


character_tokens_in_plays = {}

for play_idx in character_cleaned_dialogue_info_in_plays:
    character_tokens_in_plays[play_idx] = {}
    for character in character_cleaned_dialogue_info_in_plays[play_idx]:
        character_tokens_in_plays[play_idx][character] =             character_cleaned_dialogue_info_in_plays[play_idx][character].split()


# ### Print list of extracted characters for each play to verify against the text file

# In[35]:


for play_idx in character_tokens_in_plays:
    pprint(sorted(character_dialogue_info_in_plays[play_idx].keys()))
    print("="*100)


# ## TODO
# 
# 1. Use defaultdict to remove if for checking presence of character name in the dictionary
# 2. When adding character, convert to lower case to remove duplicates like Both, BOTH, etc.
# 3. Remove character names like All, All officers, Both, Both Citizens, etc
# 4. Token cleanup -> lowercase, remove punctuation from end, (optionally) remove stopwords
# 5. Use collections.Counter() to solve Q5. 

# ### Bonus: Demo to show usage of str.rstrip() to remove punctuation symbols at the end of tokens

# In[36]:


import string


# In[37]:


string.punctuation


# In[38]:


"clay:?!!".rstrip(string.punctuation)


# In[ ]:





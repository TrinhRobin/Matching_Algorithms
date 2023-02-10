import streamlit as st 
from util import cleaning_dataset,cleaning_dataset_int,cleaning_dataset_b2b, projects_ranking,length_without_stopwords,vader_sentiment_fr, stable_matching_algorithm_unbalanced_class,evaluate_satisfaction
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import re
st.title("Projects Attribution")
st.header("Based on mariage lemma")

options_lang = ["Français","English","B2B"]
langague_vows = st.selectbox("Please select a language/promotion:",options_lang )
uploaded_file = st.file_uploader("Please drag and drop the csv file here :",type='csv')
if uploaded_file is not None:
    # To read file as bytes:
    #bytes_data = uploaded_file.getvalue()
    #st.write(bytes_data)

    # To convert to a string based IO:
    #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    #st.write(stringio)

    # To read file as string:
    #string_data = stringio.read()
    #st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    st.write("Check that the csv file is well imported:")
    st.success('This is a success message!', icon="✅")
    df = pd.read_csv(uploaded_file)
    st.write(df.head())

    

    email_list = st.text_input("Do you want to apply a filter based on email adresses?")
    st.write(email_list )

    if langague_vows == options_lang[0]:
        df_clean = cleaning_dataset(df)
        
    if langague_vows == options_lang[1]:
        df_clean = cleaning_dataset_int(df)
    if langague_vows == options_lang[1]:
        df_clean = cleaning_dataset_b2b(df)

    st.success('This is a success message!', icon="🤖")
    number_of_vows = len(re.findall(r"Choix[0-9]{1}", ' '.join(list(df_clean.columns) )))//2
    st.write("The students' names are :")
    st.write(df_clean[["Nom","Prénom"]].reset_index(drop=True))
    

    st.write("The projects to be allocated are :")
    unique_projects = np.unique(np.concatenate([df_clean[f"Choix{i}"].unique() for i in range(number_of_vows)]))
    st.write(unique_projects)

    st.write("Congratulations ! Now let's the matching begins !")
    places ={proj : 0 for proj in   unique_projects }
    for proj in unique_projects:
        places[proj] = st.number_input(f'number of places for Project {proj} ',0,5,1)
        
  
    student_vows = {df_clean.loc[i,"Nom"]+'_'+df_clean.loc[i,"Prénom"]: [df_clean.loc[i,f'Choix{j}'] for j in range(number_of_vows) ] for i in df_clean.index}

    option_method_ranking = [r"Length (Vanilla)",r"Length Without Stopwords ",r"Sentiment Analysis (Bêta)",r"Random Dictatorship (Strategy-proof + Pareto-efficient+ Neutral)"]
    method_ranking  = st.selectbox("Choose a metric for evaluating the students' reasons : ",option_method_ranking  )
    if method_ranking== option_method_ranking [0]:
        vows_projects=projects_ranking(df=df_clean,list_projects=unique_projects,method_class1=len)
    if method_ranking== option_method_ranking [1]:
        vows_projects=projects_ranking(df=df_clean,list_projects=unique_projects,method_class1=length_without_stopwords)
    if method_ranking== option_method_ranking [2]:
        vows_projects=projects_ranking(df=df_clean,list_projects=unique_projects,method_class1=vader_sentiment_fr)
    if method_ranking== option_method_ranking [3]:
        vows_projects=projects_ranking(df=df_clean,list_projects=unique_projects,method_class1=lambda x : random.random())
    st.write( "Those are the student' vows:",student_vows)
    
    st.write("And on the opposite side, the projects' vows:",vows_projects)

    st.write("The possible places for each project is",places) 

    b =st.button("it's time for matching algorithm !")
    if b :
        st.header("Computing...please wait...")
        attributions = stable_matching_algorithm_unbalanced_class(student_vows,vows_projects,places)
        st.write("the final attributions are :", attributions)
        st.write("Is it a good matching ? Analyzing the distribution of student's vows :")

      
        fig = plt.figure()
        plt.hist(evaluate_satisfaction( student_vows ,attributions))
        plt.title("Histogram of the ranking of final projects attributions (0 = first vow, 5= last vow ")
        st.pyplot(fig)
         
        #st.write(evaluate_satisfaction( student_vows ,attributions))
       # fig = plt.figure()
        #plt.pie(evaluate_satisfaction( student_vows ,attributions), autopct='%.0f%%')
        #st.pyplot(fig)


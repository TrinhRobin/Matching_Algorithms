import streamlit as st 
from util import cleaning_dataset,projects_ranking,stable_matching_algorithm_unbalanced_class,evaluate_satisfaction
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
st.title("Projects Attribution")
st.header("Based on mariage lemma")

uploaded_file = st.file_uploader("please drag and drop the csv file here :",type='csv')
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
    df = pd.read_csv(uploaded_file)
    st.write(df.head())

    

    email_list = st.text_input("Do you want to apply a filter based on email adresses?")
    st.write(email_list )
    df_clean = cleaning_dataset(df)
    st.write("The students' names are :")
    st.write(df_clean[["Nom","Prénom"]].reset_index(drop=True))
    

    st.write("The projects to be allocated are :")
    unique_projects = np.unique(np.concatenate([df_clean["Choix1"].unique(),
                                        df_clean["Choix2"].unique(),
                                        df_clean["Choix3"].unique()]))
    st.write(unique_projects)

    st.write("Congratulations ! Now let's the matching begins !")
    places ={proj : 0 for proj in   unique_projects }
    for proj in unique_projects:
        places[proj] = st.number_input(f'number of places for Project {proj} ',0,5,1)
        
  
    student_vows = {df_clean.loc[i,"Nom"]+'_'+df_clean.loc[i,"Prénom"]: [df_clean.loc[i,f'Choix{j}'] for j in range(1,4) ] for i in df_clean.index}
    st.write( "Those are the student' vows:",student_vows)
    vows_projects=projects_ranking(df_clean,unique_projects)
    st.write("And on the opposite side, the projects' vows:",vows_projects)

    st.write("The possible places for each project is",places) 

    b =st.button("it's time for matching algorithm !")
    if b :
        st.header("Computing...please wait...")
        attributions = stable_matching_algorithm_unbalanced_class(student_vows,vows_projects,places)
        st.write("the final attributions are :", attributions)
        st.write("Is it a good matching ? Analyzing the distribution of student's vows :")

      
        fig = plt.figure()
        sns.histplot(evaluate_satisfaction( student_vows ,attributions))
        plt.title("Histogram of the ranking of final projects attributions (0 = first vow, 5= last vow ")
        st.pyplot(fig)


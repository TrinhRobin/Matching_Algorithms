import random
import pandas as pd
import numpy as np
import re
def fill_all_student_projects(list_students_projects,
                              list_all_students,
                              method_ranking ):
    student_queue = sorted([y for y in list_all_students if y not in list_students_projects], key=lambda k: method_ranking(k))
    return(list_students_projects+student_queue)

def fill_all_projects(student_vows,
                              list_all_projects,
                              method_ranking ):
    project_queue = sorted([y for y in list_all_projects if y not in student_vows], key=lambda k: method_ranking(k))
    return(student_vows+project_queue)

def cleaning_dataset(df,list_mails=[]):
    df_clean =df.drop_duplicates(subset=['Nom','Prénom'],keep='last')
    #Dropping out the rows without name/surname/email adresses 
    df_clean =  df_clean.dropna(subset=['Nom','Prénom','Adresse Mail'])
    #using regex to find number of vows :
    number_of_vows = len(re.findall(r"Donnez votre [a-z\é\è\à\ù]{1,15} choix de projet", ' '.join(list(df_clean.columns) )))
    #Wrong formating so that i neeed to reorder that :(
    df_clean_res = df_clean[list(df_clean.columns[:(3+2*number_of_vows+1)])]
    ##Filling out Empty Projects/reasons :
    df_clean_res=df_clean_res.fillna("No") 
    df_clean_res.columns = ['Horodateur', 'Nom', 'Prénom', 'Adresse_Mail' ]+\
                        [y for x in range(number_of_vows)for y in [f'Choix{x}',f'Raison_Choix{x}']]
    #using regex to dteect if theses keywords are in the columns : 
    num_column_github = [i for i,x in enumerate(list(df_clean.columns)) if re.search('github',x)][0]
    num_column_os = [i for i,x in enumerate(list(df_clean.columns)) if re.search("système d'exploitation",x)][0]
    num_column_ram= [i for i,x in enumerate(list(df_clean.columns)) if re.search('RAM',x)][0]
    
    if num_column_os:
        df_clean_res.loc[:,'OS'] = df_clean.loc[:,df_clean.columns[num_column_os]]
    if num_column_ram:
        df_clean_res.loc[:,'Memoire'] = df_clean.loc[:,df_clean.columns[num_column_ram]]
    if num_column_github:
        df_clean_res.loc[:,'Github'] = df_clean.loc[:,df_clean.columns[num_column_github]]
    #filter email adress
    if list_mails: 
        print("Filtre activé")
        df_clean_res=df_clean_res[df_clean_res['Adresse_Mail'].isin(list_mails)]
    return df_clean_res
#Adapting the preceeding function for english columns' names :

def cleaning_dataset_int(df,list_mails=[]):
    df_clean =df.drop_duplicates(subset=['Family Name','First Name'],keep='last')
    #Dropping out the rows without name/surname/email adresses 
    df_clean =  df_clean.dropna(subset=['Family Name','First Name','Email'])
    #using regex to find number of vows :
    number_of_vows = len(re.findall(r"why you choose this topic:[\.0-9]{0,2}", ' '.join(list(df_clean.columns) )))
    print( number_of_vows )
    #Wrong formating so that i neeed to reorder that :(
    df_clean_res = df_clean[list(df_clean.columns[:(3+2*number_of_vows+1)])]
    ##Filling out Empty Projects/reasons :
    df_clean_res=df_clean_res.fillna("No") 
    df_clean_res.columns = ['Horodateur', 'Nom', 'Prénom', 'Adresse_Mail' ]+\
                        [y for x in range(number_of_vows)for y in [f'Choix{x}',f'Raison_Choix{x}']]
    #filter email adress
    if list_mails: 
        print("Filtering the Mails...")
        df_clean_res=df_clean_res[df_clean_res['Adresse_Mail'].isin(list_mails)]
    return df_clean_res

def projects_ranking(df,list_projects, 
                     method_class1=len,method_class2= lambda x : random.random()):
    #A mettre en paramètre ? avec webscrapping
    list_all_students  = set([ x[0] +"_"+x[1] for x in df.loc[:,["Nom","Prénom"]].values])
    number_of_vows = len(re.findall(r"Choix[0-9]{1}", ' '.join(list(df.columns) )))//2
    for i in range(number_of_vows):
        df[f'score{i}']=df[f"Raison_Choix{i}"].apply(lambda x : method_class1(x))
    
    
    vows_projects = {project :[ x[0]+'_'+x[1] 
          for i in range(  number_of_vows) for x in df.loc[df[f"Choix{i}"]==project,].sort_values(by=f'score{i}',ascending=False).loc[:,["Nom","Prénom"]].values
                     ]
                     for project in  list_projects}
    return({ project : fill_all_student_projects(vows_projects[project], list_all_students,method_class2) for project in vows_projects})
    
def remove_student_from_waiting_list(applicant,waiting_list):
    """
    Creating a new list of the waiting_list's keys without the key applicant
    """
    return [x for x in waiting_list if x != applicant]


def update_matchings(student, choice,matchings,rankings):
    """
    Update the allocation of the project choice by adding applicant to it and then sort it according to
    the project's vows (contained in rankings)
    """
    matchings[choice].append(student)
    #Selecting the students according to the project's ranking order if they are currently match with this project
    return [x for x in rankings[choice] if x in matchings[choice]]
#be careful : inputs are modified 
def stable_matching_algorithm_unbalanced_class(student_vows, rankings, places):
    ##deep copy so as not to transform inputs !!
    #+remonving projects int the students vows of there is no places allowed for it
    students =  {key: [proj for proj in value if places[proj]]for key, value in student_vows.items()}
    #initially all the students are waiting to be assign to a project
    waiting_list = [applicants for applicants in students]
    #initially all the projects are empty (removing those without places allowed)
    matchings = {choice: [] for choice,nb_places in places.items() if nb_places }

    while waiting_list:
        for applicant in waiting_list.copy():
            if not students[applicant]:
                waiting_list = remove_student_from_waiting_list(applicant,waiting_list)
                continue
            #each student propose to his first vow
            choice = students[applicant].pop(0)
            #If the project chosen by the student still has some available places :
            if len(matchings[choice]) < places[choice]:
                matchings[choice] = update_matchings(applicant, choice,matchings,rankings)
                waiting_list = remove_student_from_waiting_list(applicant,waiting_list)
            #If not we check if the project prefers the student to its current last member and 
            # update the attributions according to the project's vows
            else:
                if rankings[choice].index(applicant) < rankings[choice].index(matchings[choice][-1]):
                    matchings[choice] = update_matchings(applicant, choice,matchings,rankings)
                    waiting_list = remove_student_from_waiting_list(applicant,waiting_list)
                    waiting_list.append(matchings[choice].pop())
   # print(waiting_list)
    return matchings

def evaluate_satisfaction(students_vows,stable_matching_results):
    student_POV = [[student, course] for student in students_vows for course, result in stable_matching_results.items() if student in result]
    return [students_vows[student_POV [i][0]].index(student_POV [i][1]) for i in range(len(student_POV))]


import streamlit as st
import dashboard_functions
import pandas as pd

# [quiz_id, ques_id, answer] --> [[quiz_id,[ques_id1, answer],[ques_id2, answer]], [], ...]
#
def match_questions_to_answers(quiz_names, answer_tuple):
    matched_answers = []
    QUIZ_ID = 0
    QUESTION_ID = 1
    ANSWER = 2

    """
    - start on the 1st element of quiz_names 
    - scan the whole tuple add all the answers to the matching quiz_id 
    - then go to the next quiz_names element
    """
        
            


    return

if __name__ == "__main__":

    all_users_data = dashboard_functions.load_users_into_objects("user_quiz_data.csv")

    # get all user names
    user_names = []
    for user in all_users_data:
        user_names.append(user.u_id)

    # Renders the side bar box
    user_selectbox = st.sidebar.selectbox('User Selection menu', user_names)

    # Select a user from the selection menu
    current_user = None
    for user in all_users_data:
        if user.u_id == user_selectbox:
            current_user = user
            break  

    # This renders the selected users dashboard and quiz data
    if current_user is not None:
        st.title(f"Dashboard for {current_user.u_id}")
        col1, col2 = st.columns(2)
        col1.metric(label = "Total Completed", value = user.completed_quiz_count)
        col2.metric(label = "Not Completed", value = len(user.quizzes_to_do))

        st.subheader("View Quiz Results")

        quiz_names = current_user.get_completed_quiz_names()
        print(quiz_names)

        if quiz_names:
            selected_quiz_id = st.selectbox("Select a completed Quiz", quiz_names)

            st.subheader(f"{selected_quiz_id} answers:")    


        else:
            st.info("This user has no completed quizzes to display.")


    

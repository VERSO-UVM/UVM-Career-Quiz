import streamlit as st
import dashboard_functions
import pandas as pd

# [quiz_id, ques_id, answer] --> [[ques_id1, answer],[ques_id2, answer]]
#
def match_quiz_to_answers(quiz_name, answer_tuple):
    all_matched_answers = [] 
    QUIZ_ID = 0
    QUESTION_ID = 1
    ANSWER_INDEX = 2

    for answer in answer_tuple:
        answer_package = []
        if answer[QUIZ_ID] == quiz_name:
            answer_package.append(answer[QUESTION_ID])
            answer_package.append(answer[ANSWER_INDEX])
            all_matched_answers.append(answer_package)
        else:
            pass
    return all_matched_answers # --> [[ques_id1, answer],[ques_id2, answer]]


def load_user_dash():
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


        if quiz_names:
            # selected_quiz_id = current quiz name that is selected
            selected_quiz_id = st.selectbox("Select a completed Quiz", quiz_names)

            st.subheader(f"{selected_quiz_id} answers:")    
            quiz_answers = match_quiz_to_answers(selected_quiz_id, user.parse_answer_tuple())

            for answer in quiz_answers:
                with st.container(border=True):
                    st.write(f"Question: {answer[0]} | Answer: {answer[1]}")
        else:
            st.info("This user has no completed quizzes to display.")    

if __name__ == "__main__":

    
    load_user_dash()
    

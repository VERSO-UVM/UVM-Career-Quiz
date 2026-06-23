import streamlit as st
import dashboard_functions
import pandas as pd

if __name__ == "__main__":

    all_users_data = dashboard_functions.load_users_into_objects("user_quiz_data.csv")

    # get all user names
    user_names = []
    for user in all_users_data:
        user_names.append(user.u_id)

    user_selectbox = st.sidebar.selectbox(
        'User Selection menu',
        user_names
    )

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
            selected_quiz = st.selectbox("Select a completed Quiz", quiz_names)
        else:
            st.info("This user has no completed quizzes to display.")

    

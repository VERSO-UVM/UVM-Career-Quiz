import sys
import json
import response_table_interaction

'''
This is the test file for takeing in a users 
completed quiz and formatting it for the data base and the dashboard
'''

def main():
    print("-> test file has started executing!")
    
    if len(sys.argv) > 1:
        raw_data = sys.argv[1]

        processed_data = response_table_interaction._json_data_convert(raw_data)
        response_table_interaction._json_data_convert(raw_data)
        print(f"-> data has been processed: {processed_data}")

''' Example of users answer package that is pasted from the POST 
('1', 
    'pjo4roy', <-- Quiz ID
    3, <-- # of questions in quiz
    [
     ('wu2k8f4', 'Answer Details: ', 'r5ms0o8', 'HELLO'), 
     ('umdk5o3', 'Answer Details: ', 'yq8rry9', 'banana'), 
     ('5u83jdb', 'Answer Details: ', '3a1mirf', 'VT')
    ]
)
    ('QuestionID', 'Answer Details: ', 'AnswerID', 'AnswerTEXT')
'''

if __name__ == '__main__':
    main()


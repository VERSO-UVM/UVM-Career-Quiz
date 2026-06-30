import sys
import json
import response_table_interaction

'''
This is the test file for takeing in a users 
completed quiz and formatting it for the data base
'''

def main():
    print("-> test file has started executing!")
    
    if len(sys.argv) > 1:
        raw_data = sys.argv[1]

        processed_data = response_table_interaction._json_data_convert(raw_data)
        print(f"-> data has been processed: {processed_data}")

if __name__ == '__main__':
    main()
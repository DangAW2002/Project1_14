import sys
sys.path.append('scr')
from prompt_custom import *
from function_call import *
from model import llama
from scr.utils import parse_and_validate_function, remove_quotes
from app_logging import LENGTH_LOGGING, error_logger, state_logger
import ast
from unidecode import unidecode

from test5 import search_data

user_assistant_prompt = [""]


def state_1(message, ):
    prompt = system_prompt(prior_system_instruction, custom_tool) + user_assistant_prompt[0] + user_prompt(message) + assistant_prompt()
    response = llama(prompt)
    print('1'*LENGTH_LOGGING)
    print("STATE 1 PROMPT")
    print(prompt)    
    print('1'*LENGTH_LOGGING)
    print("STATE 1 RESPONSE")
    print(response)
    print('1'*LENGTH_LOGGING)

    state_logger.info(f"STATE 1 | user: \n{message}\n")
    state_logger.info(f"STATE 1 | response: \n{response}\n")
    return response

def state_2_pre(func_conf):
    prompt = system_prompt(system_ins2_pre) + user_prompt(func_conf + "\nPhải có markdown table") + assistant_prompt()
    response = llama(prompt)
    print('='*LENGTH_LOGGING)
    print("STATE 2 PRE PROMPT")
    print(prompt)
    print('='*LENGTH_LOGGING)
    print("STATE 2 PRE RESPONSE")
    print(response)
    print('='*LENGTH_LOGGING)
    state_logger.info(f"STATE 2 PRE | func_conf: \n{func_conf}\n")
    state_logger.info(f"STATE 2 PRE | response: \n{response}\n")
    return response

def state_2(message):
    prompt = system_prompt(system_ins2_2, custom_tool) + user_assistant_prompt[0] + end_prompt() + user_prompt(message) + assistant_prompt()
    response = llama(prompt)
    print('2'*LENGTH_LOGGING)
    print("STATE 2 PROMPT")
    print(prompt)
    print('2'*LENGTH_LOGGING)
    print("STATE 2 RESPONSE")
    print(response)
    print('2'*LENGTH_LOGGING)
    state_logger.info(f"STATE 2 | user: \n{message}\n")
    state_logger.info(f"STATE 2 | response: \n{response}\n")
    return response

def state_3_model(message):
    prompt = (
        system_prompt(system_ins3, custom_tool)
        + user_assistant_prompt[0]
        + user_prompt("điều chỉnh")
        + assistant_prompt()
    )
    response = llama(prompt)

    state_logger.info(f"STATE 3 | response: \n{response}\n")

    print('3'*LENGTH_LOGGING)
    print("STATE 3 PROMPT")
    print(prompt)
    print("3"*LENGTH_LOGGING)
    print("STATE 3 RESPONSE:")
    print(response)
    print("3"*LENGTH_LOGGING)

    return response

def state_3_parse(response):
    function_name, args, error, error_message = parse_and_validate_function(response)
    if error:
        error_logger.error(f"Error in state_3_parse\n{error_message}\n")
        return error, error_message

    print('/'*LENGTH_LOGGING)
    print(f"Function name: {function_name}")
    print(f"Arguments: {args}")
    print('/'*LENGTH_LOGGING)

    state_logger.info(f"STATE 3 | function_name: \n{function_name}\n")
    state_logger.info(f"STATE 3 | args: \n{args}\n")

    return function_name, args

# def state_3_searchdb(function_name, args):
#     try:
#         recommend_response = ""
#         rag_data = ""
#         if function_name in search_functions:

#             arg_name = search_functions[function_name]
#             print("SEARCH FUNCTION")
#             print(arg_name)
#             print(args)

#             rag_data = search_data(args[arg_name], arg_name)
#             print(rag_data)
#             state_logger.info(f"STATE 3_2 DATABASE | query: \n{args[arg_name]}\n")
#             state_logger.info(f"STATE 3_2 DATABASE | arg_name: \n{arg_name}\n")
#             state_logger.info(f"STATE 3_2 DATABASE | rag_data: \n{rag_data}\n")

#             message = f"""Danh sách các chuỗi: {unidecode(rag_data)}\nChuỗi :{unidecode(args[arg_name].upper())}"""
#             prompt = (
#                 system_prompt(system_ins3_2_database_test)
#                 + user_prompt(message)
#                 + assistant_prompt()
#             )
#             print(prompt)
#             response_search = llama(prompt)

#             state_logger.info(f"STATE 3_2 DATABASE | response_search: \n{response_search}\n")

#             print(response_search)
#             data_list = ast.literal_eval(rag_data)
#             response_int = int(response_search)
#             print(data_list)
#             if response_int > 0 and response_int <= len(data_list):
#                 new_args = data_list[response_int - 1]
#                 # Xóa khoảng trắng đầu
#                 # new_args = new_args.strip()

#                 # # Thay thế dấu " ở đầu và cuối chuỗi
#                 # if new_args.startswith('"') and new_args.endswith('"'):
#                 #     new_args = "'" + new_args[1:-1] + "'"
#                 args = {arg_name: new_args}
#                 state_logger.info(f"STATE 3_2 DATABASE | Updated arg\nNew arg: {args}\n")

#             else:
#                 recommend_response = response_search

            
#             # response_search = remove_quotes(response_search)
            
#             # if response_search[0] == "#" and response_search[-1] == "#" and len(response_search) > 1:
#             #     response_search = response_search[1:-1]
#             #     response_search = response_search.strip("'\"")
#             #     args = {arg_name: response_search}
#             #     state_logger.info(f"STATE 3_2 DATABASE | Updated arg\nNew arg: {args}\n")
            
#             # else:
#             #     recommend_response = response_search

#             #     state_logger.info(f"STATE 3_2 DATABASE | recommend_response: \n{recommend_response}\n")
            
#         return args, recommend_response, rag_data
#     except Exception as e:
#         state_logger.error(f"Error in state_3_searchdb\n{e}\n")
#         error_logger.error(f"Error in state_3_searchdb\n{e}\n")
#         return "Error", str(e), ""

def state_3_searchdb(function_name, data):
    try:
        recommend = []
        most_similar_str = ""
        if function_name in search_functions:

            arg_name = search_functions[function_name]
            print("SEARCH FUNCTION")
            print(arg_name)
            print(data)

            most_similar, recommend = search_data(data, arg_name)
            print(most_similar)
            print(recommend)


            state_logger.info(f"STATE 3_2 DATABASE | query: \n{data}\n")
            state_logger.info(f"STATE 3_2 DATABASE | function_name: \n{function_name}\n")
            state_logger.info(f"STATE 3_2 DATABASE | arg_name: \n{arg_name}\n")
            state_logger.info(f"STATE 3_2 DATABASE | most_similar_str: \n{most_similar_str}\n")
            state_logger.info(f"STATE 3_2 DATABASE | recommend: \n{json.dumps(recommend, indent=4, ensure_ascii=False)}\n")

        return most_similar, recommend
    except Exception as e:
        state_logger.error(f"Error in state_3_searchdb\n{e}\n")
        error_logger.error(f"Error in state_3_searchdb\n{e}\n")
        return {"error": str(e)}, []

def state_3_database_recommend(query, recommend):
        recommend_str = "\n".join(json.dumps(item, ensure_ascii=False) for item in recommend)
        # arg_name = search_functions[function_name]
        print("SEARCH FUNCTION")
        user_message = f"""
Hãy dựa vào danh sách này để trả lời theo yêu cầu:
{recommend_str}

Yêu cầu: Hãy thông báo là không tìm thấy thiết bị'{query}', sau đó liệt kê danh sách trên theo kiểu gợi ý, không cần score. Phải ghi đúng y chang danh sách."""
        prompt = (
            system_prompt(system_ins3_2_database_recommend)
            + user_prompt(user_message)
            # + assistant_prompt(python_tag(f'[search_data({arg_name}={data})]') + eom_prompt() + ipython(recommend_str))
            + assistant_prompt()
        )
        print("---------------------------state_3_database_recommend---------------------------")
        print(prompt)
        response = llama(prompt)
        state_logger.info(f"STATE 3_2 DATABASE RECOMMEND | response: \n{response}\n")
        return response

def state_3_result(function_name, args):
    try:
        result = execute_function(function_name, args)
    except Exception as e:
        result = "Error", str(e)
        error_logger.error(f"""Error during execute function\nresponse: {function_name}\nFunction name: {function_name}\nArguments: {args}\nException: {str(e)}\n""")
        state_logger.error(f"STATE 3 | ERROR\n{str(e)}\n")
        return "Error", str(e)

    state_logger.info(f"STATE 3 | result: \n{result}\n")
    return result


def state_4(python_tag_str, ipython_str):
    
    prompt = system_prompt(system_ins4) + assistant_prompt(python_tag(python_tag_str)) + eom_prompt() + ipython(ipython_str) + user_prompt("Mô tả kết quả") + assistant_prompt()
    response = llama(prompt, temp= 0.1, topp=0.1)
    print('4'*LENGTH_LOGGING)
    print("STATE 4 PROMPT")
    print(prompt)
    print('4'*LENGTH_LOGGING)
    print("STATE 4 RESPONSE")
    print(response)
    print('4'*LENGTH_LOGGING)

    state_logger.info(f"STATE 4 | python_tag: \n{python_tag_str}\n")
    state_logger.info(f"STATE 4 | ipython: \n{ipython_str}\n")
    state_logger.info(f"STATE 4 | response: \n{response}\n")
    return response

def state_fix(ipython_str):
    prompt = system_prompt(system_ins_fix) + ipython(ipython_str) + assistant_prompt()
    response = llama(prompt)

    print('F'*LENGTH_LOGGING)
    print("STATE FIX PROMPT")
    print(prompt)
    print('F'*LENGTH_LOGGING)
    print("STATE FIX RESPONSE")
    print(response)
    print('F'*LENGTH_LOGGING)
    
    state_logger.info(f"STATE FIX | ipython: \n{ipython_str}\n")
    state_logger.info(f"STATE FIX | response: \n{response}")
    return response



# Dang thưc hien
def state_plot(message):
    message = "Hãy viết code vẽ biểu đồ tại đây."
    prompt = (
        system_prompt(system_ins_plot)
        + user_assistant_prompt[0]
        + user_prompt(message)
        + assistant_prompt()
    )
    response = llama(prompt)

    print('P'*LENGTH_LOGGING)
    print("STATE PLOT PROMPT")
    print(prompt)
    print('P'*LENGTH_LOGGING)
    print("STATE PLOT RESPONSE")
    print(response)
    print('P'*LENGTH_LOGGING)

    state_logger.info(f"STATE PLOT response: \n{response}")
    # try:
    #     exec(response)
    #     fig = generate_plot()
    #     return fig
    # except Exception as e:
    #     error_logger.error(str(e))
    #     return "Error", str(e)
    return response
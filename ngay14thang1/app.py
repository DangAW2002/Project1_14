import gradio as gr
from scr.prompt_custom import *
from scr.function_call import *
from scr.app_logging import LENGTH_LOGGING, error_logger, state_logger, configure_logger  # Import error_logger and state_logger from logging.py
from scr.timeout_guard import timeout_guard  # Import timeout_guard from timeout_guard.py
from scr.state import state_1, state_2_pre, state_2, state_4, state_fix, user_assistant_prompt, state_3_model, state_3_parse, state_3_result, state_3_searchdb, state_3_database_recommend  # Import state functions from state.py
import speech_recognition as sr
from pydub import AudioSegment
# Set up the global variables
state = 1
current_tool = ""

# Define the function to run the conversation
def run_conversation(message):
    global state, current_tool
    response = ""
    # Quyết định xem có thực hiện gọi hàm(tool calling) hay không
    if state == 1:
        state_logger.info('\n' + '/'*LENGTH_LOGGING + '\n') 
        # if message == "vẽ":
        #     return state_plot(message)
        response = state_1(message)
        response_tool = response
        response_tool = response_tool.replace("\n", "")
        user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt(response, end = True)

        # Kiểm tra xem response có theo cấu trúc hàm hay không
        if response_tool[0] == '[' and response_tool[-1] == ']':
            current_tool = response_tool
            state_logger.info(f"STATE 1 --> STATE 2\n")
            state = 2
            response = state_2_pre(response_tool)
            return 'Đang trong giai đoạn tùy chỉnh. Nhập "đúng" để  thực hiện công cụ hoặc "bỏ qua" để bỏ qua\n' + response
        else:
            state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
            return response
    
    # Tùy chỉnh thông số theo yêu cầu người dùng
    if state == 2:
        if message == "đúng":
            state_logger.info(f"STATE 2 | user\n{message}\n")
            state_logger.info(f"STATE 2 --> STATE 3\n")
            state = 3
        elif message == "bỏ qua":
            state = 1
            current_tool = ""
            user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt(end=True)
            state_logger.info(f"STATE | user\n {message}\n")
            state_logger.info(f"STATE 2 --> STATE 1\n")
            state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
            return "Đã bỏ qua"
        else:
            response = state_2(message)
            current_tool = response
            user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt() + response + end_prompt()
            response = state_2_pre(response)

            return 'Đang trong giai đoạn tùy chỉnh. Nhập "đúng" để  thực hiện công cụ hoặc "bỏ qua" để bỏ qua\n' + response
        
    if state == 3:
        for i in range (3):
            state = 3
            state_logger.info(f"STATE 3 & 4 | Lần: {i+1}\n")

            # Lần đầu tiên không cần chạy state_3_model
            if i:
                response = state_3_model(message)
                current_tool = response
            else:
                response = current_tool
            # Phân giải cấu trúc hàm lấy arg
            function_name, args = state_3_parse(response)

            python_tag_str = function_name
            if python_tag_str == "Error":
                continue
            # Nếu function_name thuộc search database thì thực hiện RAG
            state_logger.info(f"STATE 3 --> STATE 3_2 DATABASE\n")
            args, recommend_response = state_3_searchdb(function_name, args)
            state_logger.info(f"STATE 3_2 DATABASE --> STATE 3\n")

            if not recommend_response == '':
                state_logger.info(f"STATE 3 --> STATE 3_2 DATABASE RECOMMEND\n")
                response = state_3_database_recommend(function_name, args)
                state_logger.info(f"STATE 3_2 DATABASE RECOMMEND | response\n{response}\n")
                state_logger.info(f"STATE 3_2 DATABASE RECOMMEND --> STATE 3\n")
                response = "Tôi không tìm thấy thông tin bạn yêu cầu. Dưới đây là một số thông tin tương tự:\n" + response
                user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt(response, end=True) 

                state = 1
                current_tool = ""
                state_logger.info(f"STATE 3 --> STATE 1\n")
                state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
                return response
            # Thực thi hàm công cụ và lấy kết quả JSON
            ipython_str  = state_3_result(function_name, args)
            

            state = 4

            print("---------------------------------------------------")
            print("STATE 4")
            print(f"Lần: {i+1}")
            state_logger.info(f"STATE 3 --> STATE FIX\n")

            # Kiểm tra status là Error hay Success
            check = state_fix(ipython_str)
            print("check RESPONSE")
            print(check)

            state_logger.info(f"STATE FIX --> STATE 4\n")
            response = state_4(python_tag_str, ipython_str)
            user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt(python_tag(python_tag_str)) + eom_prompt() + ipython(ipython_str)
            user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt("Mô tả kết quả") + assistant_prompt(response, end = True)

            print("---------------------------------------------------")
            print("STATE 4")
            print(user_assistant_prompt[0])

            # Nếu lỗi thì thực hiện lại vòng lặp để tự sửa lỗi
            if check == "Error" or check == '"Error"':
                message = "Sửa lại lỗi và gọi lại công cụ. Không viết thêm văn bản."
                state_logger.info(f"STATE 4 --> STATE 3\n")
            else:
            # Nếu thành công thì hiển thị kết quả và kết thúc 
                state = 1
                current_tool = ""
                state_logger.info(f"STATE 4 --> STATE 1\n")
                state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 

                return response
            
        # Lỗi tại lúc chạy model và phân giải hàm
        if python_tag_str == "Error":
            state = 1
            current_tool = ""
            response = "Đã có lỗi xảy ra trong lúc dùng công cụ, quay về mặc định."
            user_assistant_prompt[0] = user_assistant_prompt[0] + user_prompt(message) + assistant_prompt(response, end=True) 
            state_logger.info(f"STATE 3 | ERROR\n Có lỗi tại state 3\n")
            state_logger.info(f"STATE 3 --> STATE 1\n")
            state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
            return response
        # Lỗi tại lúc check == Error <==> Thường là sai format
        else:
            response = response + "\n\nQuay về mặc định."
            state = 1
            current_tool = ""
            state_logger.info(f"STATE 4 | ERROR \n Có lỗi tại state 4\n")
            state_logger.info(f"STATE 4 --> STATE 1\n")
            state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
            return response
        
# Hàm gradio_interface với timeout
def gradio_interface(message, history):
    def process_message():  # Gói logic của bạn trong hàm này
        global state
        response = run_conversation(message)
        return response

    try:
        # Thêm cơ chế timeout vào hàm chính
        response = timeout_guard(process_message, timeout=120)  # Giới hạn thời gian 120 giây
    except Exception as e:
        print(e)
        response = str(e) + ' Vui lòng nhấn "Reset Chat" để bắt đầu lại.'
        state_logger.info(f"STATE {state} | ERROR\n{str(e)}\n")
        state_logger.info(f"STATE {state} --> STATE 1\n")
        state_logger.info('\n' + '\\'*LENGTH_LOGGING + '\n') 
        error_logger.error(str(e) + '\n')
        reset_chat()  # Reset chat
    return response

# Define your custom button functionality (reset chat)
def reset_chat():
    global state, current_tool
    state = 1
    current_tool = ""
    user_assistant_prompt[0] = ""
    return []  # Return empty message and empty chat history to reset

# Define the function to convert voice input to text
def voice_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    print(f"Audio file path: {audio_file_path}")
    if audio_file_path is None:
        return ''
    # Chuyển đổi sang WAV 16kHz mono nếu cần
    audio = AudioSegment.from_file(audio_file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)  # Thiết lập 16kHz và mono
    audio.export("converted_audio.wav", format="wav")
    audio_file_path = "converted_audio.wav"
    print("-"*50)
    print(f"Converted audio file path: {audio_file_path}")
    with sr.AudioFile(audio_file_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Loại bỏ nhiễu
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")  # Assuming Vietnamese language
        print(f"User said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return 'Could not understand the audio.'
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
        return f'Error with the speech recognition service: {e}'


text_input = gr.Textbox(lines=1, label="Nhập tin nhắn để hỏi AI", submit_btn=True)

with gr.Blocks(fill_height=True) as demo:
    # Define the chat interface with a variable-based text input
    iface = gr.ChatInterface(
        fn=gradio_interface,
        type="messages",
        title="Llama AI Assistant",
        description="Ask questions to the AI Assistant.",
        examples=[
            "Bạn là ai?",
            "tôi muốn biết thời tiết ở Hà Nội",
            "Thiết lập máy chủ tên 'Server1' với IP '192.168.1.1', cổng 8080, hệ điều hành 'Linux', 4 lõi CPU, 16GB RAM, 256GB lưu trữ",
            "thời tiết tại 'Hanoi' từ '2024-12-16 08:00:00' đến '2024-12-16 12:00:00'",
            "Cài đặt lại thiết bị zxc1",
            "Reset device2",
            "Cấu hình tốc độ lấy mẫu",
            "Cấu hình tốc độ gửi cho thiết bị system1",
            "Cập nhật thời gian",
            "Update phần mềm",
            "Lấy thông tin thiết bị f 16020",
            "Lấy thông tin thiết bị f-16020",
            "Lấy thông tin thiết bị F122334",
            "Lấy thông tin thiết bị F16021",
            "Lấy thông tin thiết bị f@16020",
            "Lấy thông tin thiết bị F-16020",
            "tìm thông tim thiết bị quang trung - xô viết",
            "lấy thông tin thiết bị đồng hồ nguyễn công trứ",
        ],
        textbox=text_input
    )

    # Add a button to reset chat
    button = gr.Button("Reset Chat", elem_id="reset_button")
    button.click(reset_chat, outputs=iface.chatbot)

    # Add a file input for voice input
    voice_input = gr.Audio(sources=["microphone","upload"], type="filepath", label="Voice Input",format="wav")
    voice_input.change(fn=voice_to_text, inputs=voice_input, outputs=text_input)

if __name__ == "__main__":
    configure_logger()  # Configure logger
    demo.launch(server_name="0.0.0.0", server_port=8080,share= True)  # Launch the interface
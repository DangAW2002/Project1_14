from pydub import AudioSegment

# Đọc file WAV 44kHz
audio = AudioSegment.from_wav("000000.wav")

# Chuyển đổi tần số lấy mẫu về 16kHz
audio_16khz = audio.set_frame_rate(16000)

# Lưu file mới
audio_16khz.export("output_16khz.wav", format="wav")

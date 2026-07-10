import google.generativeai as genai
genai.configure(api_key="AIzaSyBevXx1IboO3jdUuxkx4OXCIf9o48QNpZs")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error:", e)

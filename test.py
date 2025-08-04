# import google.generativeai as genai

# # Replace this with your actual API key
# GOOGLE_API_KEY = "AIzaSyBMUcv4SGNZ3t9SQqY2Qen-8-Y5PlDfuW0"

# genai.configure(api_key=GOOGLE_API_KEY)

# # Load the Gemini model
# model = genai.GenerativeModel('gemini-2.0-flash')

# # Send a prompt
# response = model.generate_content("in describtive way what's this multilingual model?",stream=True)
# for chunk in response:
#     print(chunk.text)
# print(response.text)
import test2
import platform
import datetime
class MyClass():
    """docstring for MyClass."""
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def __str__(self):
        return f"{self.name} {self.age}"
    
    def getName(self):
        return self.name
    def getAge(self):
        return self.age
    def setName(self,name):
        self.name = name
    def setAge(self,age):
        self.age = age
   
obj = MyClass("John", 30)
print(obj.getName())  # Output: John
print(obj.getAge())   # Output: 30

obj2 = MyClass("Mohamed", 31)

print(obj2.getName())  # Output: Mohamed
print(obj2.getAge())   # Output: 31

obj.setName("Doe")
obj.setAge(25)

print(obj)  # Output: Doe
print(obj2)   # Output: 25

a = test2
print(a.myFun())

x = platform.system()
print(x)
print(dir(a))
x = datetime.datetime.now()
print(x)
import json

# some JSON:
x =  '{ "name":"John", "age":30, "city":"New York"}'

# parse x:
y = json.loads(x)

# the result is a Python dictionary:
print(y)
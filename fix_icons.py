import re

with open("app.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

content = re.sub(r'page_icon="[^"]*"', lambda m: 'page_icon="\\U0001F393"', content)
content = re.sub(r'title="User Interface", icon="[^"]*"', lambda m: 'title="User Interface", icon="\\U0001F4AC"', content)
content = re.sub(r'title="Admin Interface", icon="[^"]*"', lambda m: 'title="Admin Interface", icon="\\U0001F4CA"', content)
content = re.sub(r'title="Live Admin Interface", icon="[^"]*"', lambda m: 'title="Live Admin Interface", icon="\\U0001F534"', content)
content = re.sub(r'title="Settings", icon="[^"]*"', lambda m: 'title="Settings", icon="\\u2699\\uFE0F"', content)

with open("app.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("Done")
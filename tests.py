import re

text ="a dragon --ratio 2:1 running in a forest"

pattern = r'--(\w+)\s+([^\s]+)'
flags = re.findall(pattern, text)
print(flags)

print(re.sub(pattern, '', text).strip())
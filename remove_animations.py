import re

# Read the file
with open('templates/core/home_new.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all data-aos attributes
content = re.sub(r'\s*data-aos(?:-[a-z]+)?="[^"]*"', '', content)

# Write back
with open('templates/core/home_new.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Removed all data-aos animation attributes')
print('✅ Page will load much faster now!')

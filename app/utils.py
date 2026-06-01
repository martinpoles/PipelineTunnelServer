import re

def sanitize_filename(name):

    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    name = re.sub(r'\s+', ' ', name)

    return name.strip()
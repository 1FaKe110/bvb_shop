import os
import re

additional = """
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
"""
domain = 'test-bvb-shop.ru'
docker_ip = '172.17.0.2'
port = 1111

# Открываем файл app.py и читаем содержимое
with open('app.py', 'r') as file:
    content = file.read()

# Ищем все декораторы @app.route
routes = re.findall(r"@app.route\(['\"](.*?)['\"].*?\)", content)


# Генерируем конфигурацию для Nginx
nginx_config = "server {\n"
nginx_config += "    listen 443 ssl;\n"
nginx_config += f"    server_name {domain};\n\n"
nginx_config += "    ssl_certificate /etc/nginx/certs/certificate.pem;\n"
nginx_config += "    ssl_certificate_key /etc/nginx/certs/private.key;\n\n"

for route in routes:
    location = route if '<' not in route else re.sub(r'/<.*?>', r'/*', route)
    nginx_config += f"    location {location} {{\n"
    nginx_config += f"        proxy_pass http://{docker_ip}:{port}" + re.sub(r'<\w+>', '*', route) + ";"
    nginx_config += additional
    nginx_config += "    }\n"

nginx_config += "}\n"

print(nginx_config)
with open('/etc/nginx/sites-enabled/shop', 'w', encoding='utf-8') as f:
    f.write(nginx_config)

print(os.popen('nginx -t').read())

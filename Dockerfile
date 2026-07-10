FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
#COPY pyinstaller.spec .

#RUN pip install --no-cache-dir pyinstaller==6.21.0 && \
#    pyinstaller pyinstaller.spec --clean && \
#    rm -rf /app/build /app/*.spec

#--from=frontend-builder 表示从虚拟机内部复制
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["sh", "-c", "nginx && python /app/backend/app.py"]

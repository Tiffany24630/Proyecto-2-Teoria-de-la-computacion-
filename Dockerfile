# Etapa 1: Build de React
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Etapa 2: Python Backend con el bundle de React
FROM python:3.11-slim
WORKDIR /app

# Copiar código de backend y gramáticas
COPY *.py ./
COPY ejemplos/ ./ejemplos/

# Copiar el build compilado de React
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 5000
ENV PORT=5000

CMD ["python", "app.py"]

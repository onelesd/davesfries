FROM python:3.13-alpine AS build
WORKDIR /work
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY build.py template.html ./
COPY movies/ movies/
COPY assets/ assets/
RUN python build.py

FROM nginx:alpine
COPY --from=build /work/dist/ /usr/share/nginx/html/

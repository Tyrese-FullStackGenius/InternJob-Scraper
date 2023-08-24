#FROM node:16-alpine3.16 as builder
#RUN mkdir -p /app
#WORKDIR /app
#COPY package.json .
#RUN npm i
#COPY . .
#RUN npm run build:prod
#
#FROM socialengine/nginx-spa:latest
#COPY --from=builder /app/dist/demo1 /app

# ARM 64
FROM arm64v8/node:14.21.3-slim as builder
RUN mkdir -p /app
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm i
COPY . .
RUN npm run build:prod

FROM arm64v8/nginx:1.22-perl
RUN rm -rf /etc/nginx/conf.d
RUN mkdir -p /etc/nginx/conf.d
COPY ./default.conf /etc/nginx/conf.d/
COPY --from=builder /app/dist/demo1 /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

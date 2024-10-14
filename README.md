# Loki Logger 

This repository is a reference repository to configuring a logger which can send logs to Loki with structured metadata enabled in your application.

## NestJS

Refer: [nestjs](./nestjs/)

This folder contains a small reference NestJS application which configures the Loki Logger to send logs to Loki with structured metadata.

TL;DR: Copy the [nestjs/src/logger](./nestjs/src/logger/) folder in your app.
Configure the logger in you `app.module.ts` similar to [app.module.ts](./nestjs/src/app.module.ts)

and voila!

## Python

Refer: [python](./python/)

This folder contains a small reference Python application which configures the Loki Logger to send logs to Loki with structured metadata.


## Running the samples locally

1. Start the loki and grafana instances with promtail
```bash
cd docker-loki
docker-compose up -d
```

### For NestJS

2. Navigate to the `nestjs` folder and install the dependencies
```bash
cd nestjs
npm install
```

3. Run the application
```bash
npm run start
```

### For Python

2. Navigate to the `python` folder and install the dependencies
```bash
cd python
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```


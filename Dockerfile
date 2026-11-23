# syntax=docker/dockerfile:1
# Runs run.bat's pipeline once and exits: the TypeScript pre-processing turns ramen-ratings.csv into
# ramen-ratings.json and ramen-info.json, then neural-network.py trains, tests and prints the results.
FROM node:22-slim AS pre
WORKDIR /app/pre-processing
COPY pre-processing/package.json pre-processing/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY pre-processing/tsconfig.json pre-processing/main.ts ./
RUN npx tsc

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Only the node binary is needed to run the compiled pre-processing script.
COPY --from=pre /usr/local/bin/node /usr/local/bin/node
COPY --from=pre /app/pre-processing/dist /app/pre-processing/dist
COPY ramen-ratings.csv ./
COPY neural-network /app/neural-network
WORKDIR /app/pre-processing
CMD ["sh", "-c", "node dist/main.js && python ../neural-network/neural-network.py"]

FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g firebase-tools

WORKDIR /firebase

COPY firebase.json .
COPY seed-users.sh .
RUN chmod +x seed-users.sh

EXPOSE 9099 4000

CMD ["sh", "-c", "firebase emulators:start --project ${FIREBASE_PROJECT_ID:-fbi-dev-484410} & ./seed-users.sh && wait"]

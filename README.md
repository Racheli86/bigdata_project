# PubMed Big Data Search and AI Question-Answering Pipeline

This project implements an end-to-end streaming data pipeline for 1,000 semi-structured PubMed question-and-answer records.

The records are read from a JSON Lines dataset, streamed through Apache Kafka, transformed by a Python consumer, and indexed in Elasticsearch. A FastAPI application provides keyword search and an AI-powered retrieval-augmented generation (RAG) endpoint using Google Gemini.

## Architecture

```text
pubmed_data.json
        |
        v
   producer.py
        |
        v
 Apache Kafka
(pubmed_topic)
        |
        v
   consumer.py
        |
        v
 Transformation
        |
        v
 Elasticsearch
(pubmed-index)
        |
        v
 search_engine.py
        |
        v
 FastAPI
 /search and /ask
        |
        v
 Gemini RAG answer
```

## Technologies

- Python
- Docker and Docker Compose
- Apache ZooKeeper
- Apache Kafka
- Elasticsearch
- FastAPI
- Uvicorn
- Google Gemini API
- JSON Lines data

## Dataset

The project uses `pubmed_data.json`, which contains 1,000 PubMed question-and-answer records.

Each line is a JSON object that may contain:

- `pmid` — PubMed article identifier
- `question` — research question
- `context` — article context or abstract
- `long_answer` — article conclusion
- `final_decision` — answer classification such as `yes`, `no`, or `maybe`
- `labels` — additional dataset labels

The dataset is semi-structured because every record is stored as JSON. It also contains unstructured medical text in fields such as `question`, `context`, and `long_answer`.

## Data pipeline

The pipeline performs the following steps:

1. `producer.py` reads the 1,000 records from `pubmed_data.json`.
2. The producer publishes every record to the Kafka topic `pubmed_topic`.
3. `consumer.py` listens to the same Kafka topic.
4. The consumer transforms each record.
5. The transformed records are indexed in the Elasticsearch index `pubmed-index`.
6. `search_engine.py` retrieves relevant documents from Elasticsearch.
7. `app.py` exposes the system through a FastAPI application.
8. `answer_generator.py` supplies the retrieved evidence to Gemini.
9. Gemini generates an answer grounded in the retrieved PubMed records and includes PMID citations.

## Data transformation

Before indexing each record, the consumer creates additional useful fields:

- `context_word_count` — the number of words in the article context
- `has_long_answer` — indicates whether the record contains a long answer
- `search_text` — combines searchable text fields into one field
- Normalized `final_decision` values

These transformations make the records easier to search, validate, and analyse.

## Project files

- `docker-compose.yml` — starts Kafka, ZooKeeper, and Elasticsearch
- `pubmed_data.json` — the 1,000-record PubMed dataset
- `producer.py` — publishes the dataset to Kafka
- `consumer.py` — consumes, transforms, and indexes records
- `search_engine.py` — performs Elasticsearch retrieval
- `answer_generator.py` — generates grounded Gemini answers
- `app.py` — provides the FastAPI endpoints
- `insights.py` — calculates dataset statistics and insights
- `load_data.py` — downloads or prepares the dataset
- `seed_search_demo.py` — loads a small demonstration dataset
- `requirements.txt` — lists the Python dependencies

## Prerequisites

Before running the project, install:

- Git
- Python 3.12 or another compatible Python 3 version
- Docker Desktop

Docker Desktop must be open and running before starting the services.

A Gemini API key is required only for the `/ask` endpoint. The `/search` endpoint works without an API key.

## Installation

Clone the team repository:

```bash
git clone https://github.com/Racheli86/bigdata_project.git
cd bigdata_project
```

Create a virtual environment.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
python -m pip install confluent-kafka pandas
```

The second command installs the packages required by `producer.py` and `load_data.py`.

## Running the complete pipeline

The pipeline uses multiple terminal windows. Run all commands from the cloned project directory.

### Step 1: Start Docker services

Make sure Docker Desktop is running, then execute:

```bash
docker compose up -d
docker compose ps
```

The output should show these three services running:

- ZooKeeper on port `2181`
- Kafka on port `9092`
- Elasticsearch on port `9200`

The warning that the Docker Compose `version` attribute is obsolete can be ignored.

Check Elasticsearch:

```bash
curl http://localhost:9200
```

### Step 2: Start the consumer

Open Terminal 1.

#### macOS or Linux

```bash
cd ~/bigdata_project
source .venv/bin/activate
python consumer.py
```

#### Windows PowerShell

```powershell
cd path\to\bigdata_project
.venv\Scripts\Activate.ps1
python consumer.py
```

Expected output:

```text
Connected to Elasticsearch.
Created index: pubmed-index
Connected to Kafka.
Listening to Kafka topic: pubmed_topic
```

Leave this terminal running.

### Step 3: Run the producer

Open Terminal 2.

#### macOS or Linux

```bash
cd ~/bigdata_project
source .venv/bin/activate
python producer.py
```

#### Windows PowerShell

```powershell
cd path\to\bigdata_project
.venv\Scripts\Activate.ps1
python producer.py
```

The producer should send all 1,000 records to Kafka and finish with a message similar to:

```text
All 1000 records have been successfully sent to Kafka!
```

The consumer terminal should display:

```text
Indexed 100 records...
Indexed 200 records...
...
Indexed 1000 records...
```

### Step 4: Verify Elasticsearch

Open Terminal 3 and run:

```bash
curl http://localhost:9200/pubmed-index/_count
```

The response should contain:

```json
{
  "count": 1000
}
```

This confirms that all 1,000 records completed the following route:

```text
JSON → Producer → Kafka → Consumer → Transformation → Elasticsearch
```

## Dataset insights

To calculate statistics from the dataset, run:

```bash
python insights.py
```

Expected results include:

```text
Total records: 1000
Average context length: approximately 200 words
Records with long answers: 1000
```

The final-decision distribution is:

- `yes`: 552 records
- `no`: 338 records
- `maybe`: 110 records

## Running the API

Open another terminal and activate the virtual environment.

### Run without Gemini

The keyword search endpoint does not require an API key:

```bash
python -m uvicorn app:app --reload --port 8002
```

### Run with Gemini on macOS or Linux

Set the API key as an environment variable without saving it in the source code:

```bash
read -s "GEMINI_API_KEY?Paste your Gemini API key: "
export GEMINI_API_KEY
echo
python -m uvicorn app:app --reload --port 8002
```

### Run with Gemini on Windows PowerShell

```powershell
$env:GEMINI_API_KEY="PASTE_YOUR_KEY_HERE"
python -m uvicorn app:app --reload --port 8002
```

Never save a real Gemini API key in the source code or commit it to GitHub.

Open the interactive API documentation:

[http://localhost:8002/docs](http://localhost:8002/docs)

## API endpoints

### `GET /`

Returns basic information about the API.

### `POST /search`

Runs keyword-based retrieval against Elasticsearch.

Example request:

```json
{
  "query": "mitochondria lace plant",
  "top_k": 3
}
```

The response includes the most relevant PubMed documents and their Elasticsearch relevance scores.

### `POST /ask`

Implements the AI-powered RAG workflow.

Example request:

```json
{
  "query": "Do mitochondria play a role in programmed cell death in lace plant leaves?",
  "top_k": 3
}
```

The endpoint:

1. Searches Elasticsearch for relevant PubMed records.
2. Supplies the retrieved records to Gemini as evidence.
3. Instructs Gemini to answer using only the retrieved evidence.
4. Returns the generated answer.
5. Includes PMID citations and the retrieved documents.

A successful response should have HTTP status `200` and include an answer citing a source such as:

```text
[PMID: 21645374]
```

If the retrieved documents do not contain enough information, the system returns:

```text
The retrieved articles do not provide enough evidence.
```

## AI capability: Retrieval-Augmented Generation

The required AI capability is retrieval-augmented generation (RAG).

RAG combines information retrieval with a generative language model:

1. A user asks a natural-language question.
2. Elasticsearch retrieves relevant PubMed records.
3. The retrieved records become the evidence supplied to Gemini.
4. Gemini generates an answer grounded in that evidence.
5. PMID citations connect the generated answer to its sources.

This approach reduces unsupported answers because Gemini is instructed to use only evidence retrieved from the project dataset.

The keyword retrieval results and the AI-generated answer remain separate in the API response, making it possible to inspect the evidence used by the model.

## Stopping the project

Stop the consumer and Uvicorn by pressing `Control + C` in their respective terminals.

Stop the Docker services:

```bash
docker compose down
```

This stops and removes the project containers. If the Elasticsearch data is not retained, run the consumer and producer again during the next clean start to recreate the index.

## Troubleshooting

### Port already allocated

If Docker reports that port `9200`, `9092`, or `2181` is already allocated, find the containers currently using the ports:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Stop the old containers using their names:

```bash
docker stop CONTAINER_NAME
```

Then start this project again:

```bash
docker compose up -d
```

### Consumer is listening but receives nothing

Confirm that both files use exactly the same Kafka topic:

```text
pubmed_topic
```

Start the consumer before running the producer.

### Elasticsearch contains 2,000 records

This can happen if the producer is run multiple times and documents are indexed without stable identifiers. For a completely clean test, stop the project and remove its stored Docker data:

```bash
docker compose down -v
docker compose up -d
```

Then run the consumer and producer once.

Warning: `docker compose down -v` permanently deletes Docker volumes belonging to this project.

### Gemini API key is missing

Set `GEMINI_API_KEY` in the same terminal in which Uvicorn is started. Do not place the key directly in `app.py` or `answer_generator.py`.

### Localhost refuses to connect

Confirm that Uvicorn is still running and open:

[http://localhost:8002/docs](http://localhost:8002/docs)

If port `8002` is unavailable, use another port:

```bash
python -m uvicorn app:app --reload --port 8003
```

Then open:

[http://localhost:8003/docs](http://localhost:8003/docs)

## Security

- Never commit a Gemini API key to GitHub.
- Store secrets only in environment variables or an ignored `.env` file.
- The PubMed dataset used in this project is public and does not contain private user information.
- AI answers should be treated as generated summaries of the retrieved records, not as medical advice.

## Demonstrated result

The complete pipeline was tested successfully:

- All three Docker services started.
- The producer sent 1,000 PubMed records.
- The consumer transformed and indexed 1,000 records.
- Elasticsearch reported exactly 1,000 documents.
- The `/search` endpoint returned relevant PubMed articles.
- The `/ask` endpoint returned a Gemini-generated answer grounded in retrieved evidence.
- The answer included PMID source citations.

## Repository

Team repository:

[https://github.com/Racheli86/bigdata_project](https://github.com/Racheli86/bigdata_project)

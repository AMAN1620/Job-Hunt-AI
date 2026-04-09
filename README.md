# Job-Hunt-AI

An AI-powered job finder that matches candidates to relevant job openings based on their resume. Upload a PDF resume, and the system extracts your skills and experience, then crawls major job boards to surface matching positions.

## How It Works

1. **Upload your resume** — PDF text is extracted and parsed by GPT-3.5-turbo to identify your skills, location, and years of experience.
2. **Generate a session token** — A unique token is issued to track your session and cache results.
3. **Search for jobs** — Provide a job title, location, and experience level. The system uses Firecrawl to crawl Naukri, Indeed, and Monster for matching openings.
4. **Get results** — Structured job listings (company, role, experience required, application link) are returned and cached in Redis.

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Resume Parsing | OpenAI GPT-3.5-turbo |
| Job Crawling | Firecrawl |
| PDF Extraction | pdfplumber |
| Caching | Redis |
| Observability | Langfuse (optional) |
| Containerization | Docker |

## Project Structure

```
Job-Hunt-AI/
├── src/
│   ├── main.py                  # FastAPI app and CORS config
│   ├── api/
│   │   └── routes.py            # All API endpoints
│   ├── services/
│   │   ├── pdf_parse.py         # PDF extraction + GPT parsing
│   │   ├── job_search.py        # Firecrawl job search agent
│   │   └── agno_agent.py        # Experimental DuckDuckGo agent
│   ├── models/
│   │   ├── job_search_model.py  # Pydantic schemas
│   │   └── fire_crawl_model.py  # Firecrawl response schema
│   └── redis_module/
│       ├── config.py            # Redis connection
│       ├── cache.py             # Cache read/write
│       └── records.py           # Session data models
├── deployments/
│   └── Dockerfile
├── run_server.py                # Server entry point
├── requirements.in              # Direct dependencies
└── requirements.txt             # Pinned dependencies
```

## API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs available at `http://localhost:8000/docs`.

### `GET /health_check/`
Returns `{"message": "App is running!!"}`.

### `POST /generate_token/`
Creates a session token for caching results.

**Response:**
```json
{ "token": "uuid-string" }
```

### `POST /pdf_data_extract/`
Uploads a resume PDF and returns structured profile data.

**Request:** `multipart/form-data` with `resume` file field.

**Response:**
```json
{
  "location": "New York, USA",
  "skills": ["Python", "Machine Learning", "React"],
  "years_of_experience": 5
}
```

### `POST /find_jobs/?token=<token>`
Searches for matching jobs based on provided criteria.

**Request body:**
```json
{
  "job_title": "Software Engineer",
  "skills": ["Python", "FastAPI"],
  "experience": 3,
  "location": "Bangalore",
  "remote_only": false
}
```

**Response:** Array of job postings:
```json
[
  {
    "company_name": "Google",
    "region": "West Coast",
    "role": "Backend Developer",
    "job_title": "Senior Software Engineer",
    "experience": "3-5 years",
    "job_link": "https://..."
  }
]
```

Results are cached in Redis against the session token. Returns 5–30 results.

## Setup

### Prerequisites

- Python 3.10+
- Redis instance (local or Redis Cloud)
- API keys: [OpenAI](https://platform.openai.com/), [Firecrawl](https://www.firecrawl.dev/)

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-key
FIRE_CRAWL_API_KEY=your-firecrawl-key
MODEL=gpt-3.5-turbo

REDIS_HOST=your-redis-host
REDIS_PORT=your-redis-port
REDIS_PASSWORD=your-redis-password
REDIS_USER=default
REDIS_CONNECTION_URL=redis://default:password@host:port

# Optional — LLM observability
LANGFUSE_SECRET_KEY=your-langfuse-secret
LANGFUSE_PUBLIC_KEY=your-langfuse-public
```

### Local Development

```bash
# Clone and enter the project
git clone <repo-url>
cd Job-Hunt-AI

# Create and activate a virtual environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run_server.py
```

Server starts at `http://localhost:8000`.

### Docker

```bash
# Build the image
docker build -f deployments/Dockerfile -t job-hunt-ai:latest .

# Run the container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=<key> \
  -e FIRE_CRAWL_API_KEY=<key> \
  -e REDIS_CONNECTION_URL=<url> \
  job-hunt-ai:latest
```

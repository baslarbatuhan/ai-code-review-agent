# 📚 API Documentation - AI-Powered Code Review Agent

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Last Updated:** December 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Request/Response Formats](#requestresponse-formats)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

The AI-Powered Code Review Agent API provides RESTful endpoints for:
- Creating code reviews
- Retrieving review results
- Managing review history
- Accessing analytics and statistics

All endpoints return JSON responses and follow RESTful conventions.

---

## Authentication

Currently, the API does not require authentication for local development. For production deployments, implement API keys or OAuth2.

**Future:** API key authentication will be added in version 2.0.

---

## Base URL

```
http://localhost:8000/api/v1
```

**Production:** Replace `localhost:8000` with your production server URL.

---

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T10:30:00",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - API is healthy

---

### 2. Create Review

Create a new code review for a file, directory, commit, or pull request.

**Endpoint:** `POST /reviews`

**Request Body:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "commit_sha": null,
  "pull_request_id": null,
  "agent_types": null,
  "scan_entire_repo": false
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repository_url` | string | Yes | GitHub repository URL |
| `file_path` | string | No | Path to file (relative to repo root) |
| `commit_sha` | string | No | Commit SHA to review |
| `pull_request_id` | integer | No | Pull request number |
| `agent_types` | array | No | Agent types to run (quality, security, performance, documentation) |
| `scan_entire_repo` | boolean | No | Scan entire repository (default: false) |

**Priority Order:**
1. `file_path` (highest priority)
2. `commit_sha`
3. `pull_request_id`
4. `scan_entire_repo`

**Example Requests:**

**Single File:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/python/cpython",
    "file_path": "Lib/os.py"
  }'
```

**Directory Scan:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/owner/repo",
    "file_path": "src/utils"
  }'
```

**Entire Repository:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/owner/repo",
    "scan_entire_repo": true
  }'
```

**Pull Request:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/owner/repo",
    "pull_request_id": 5
  }'
```

**Specific Agents:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/owner/repo",
    "file_path": "src/main.py",
    "agent_types": ["quality", "security"]
  }'
```

**Response:**
```json
{
  "review_id": 1,
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "status": "completed",
  "results": [
    {
      "agent_type": "quality",
      "success": true,
      "execution_time": 2.5,
      "issues": [
        {
          "severity": "medium",
          "issue_type": "C0111",
          "message": "Missing docstring",
          "line_number": 10,
          "suggestion": "Add docstring to function",
          "metadata": {
            "tool": "pylint"
          }
        }
      ],
      "error_message": null,
      "metadata": {
        "agent_type": "quality",
        "version": "1.0.0"
      }
    },
    {
      "agent_type": "security",
      "success": true,
      "execution_time": 1.8,
      "issues": [],
      "error_message": null,
      "metadata": {}
    }
  ],
  "total_issues": 5,
  "created_at": "2025-12-24T10:30:00",
  "completed_at": "2025-12-24T10:30:05"
}
```

**Status Codes:**
- `200 OK` - Review completed successfully
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - File/repository not found
- `500 Internal Server Error` - Server error

---

### 3. Get Review

Retrieve details of a specific review by ID.

**Endpoint:** `GET /reviews/{review_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `review_id` | integer | Yes | Review ID |

**Example:**
```bash
curl http://localhost:8000/api/v1/reviews/1
```

**Response:**
```json
{
  "review_id": 1,
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "status": "completed",
  "results": [...],
  "total_issues": 5,
  "created_at": "2025-12-24T10:30:00",
  "completed_at": "2025-12-24T10:30:05"
}
```

**Status Codes:**
- `200 OK` - Review found
- `404 Not Found` - Review not found

---

### 4. List Reviews

List all reviews with pagination and filtering.

**Endpoint:** `GET /reviews`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Number of results per page |
| `offset` | integer | No | 0 | Number of results to skip |
| `repository_url` | string | No | - | Filter by repository URL |
| `status` | string | No | - | Filter by status (pending, completed, failed) |

**Example:**
```bash
# Get first 20 reviews
curl "http://localhost:8000/api/v1/reviews?limit=20&offset=0"

# Filter by repository
curl "http://localhost:8000/api/v1/reviews?repository_url=https://github.com/owner/repo"

# Filter by status
curl "http://localhost:8000/api/v1/reviews?status=completed"
```

**Response:**
```json
{
  "reviews": [
    {
      "review_id": 1,
      "repository_url": "https://github.com/owner/repo",
      "file_path": "src/main.py",
      "status": "completed",
      "total_issues": 5,
      "created_at": "2025-12-24T10:30:00",
      "completed_at": "2025-12-24T10:30:05"
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

**Status Codes:**
- `200 OK` - Success

---

### 5. Get Analytics

Get review statistics and metrics.

**Endpoint:** `GET /reviews/analytics`

**Example:**
```bash
curl http://localhost:8000/api/v1/reviews/analytics
```

**Response:**
```json
{
  "total_reviews": 50,
  "total_issues": 250,
  "severity_stats": {
    "critical": 5,
    "high": 20,
    "medium": 100,
    "low": 125
  },
  "agent_stats": {
    "quality": {
      "total_issues": 100,
      "avg_execution_time": 2.5
    },
    "security": {
      "total_issues": 50,
      "avg_execution_time": 1.8
    },
    "performance": {
      "total_issues": 60,
      "avg_execution_time": 2.2
    },
    "documentation": {
      "total_issues": 40,
      "avg_execution_time": 1.5
    }
  },
  "repo_stats": {
    "total_repositories": 10,
    "most_reviewed": "https://github.com/owner/repo"
  },
  "recent_reviews_count": 15,
  "success_rate": 0.95
}
```

**Status Codes:**
- `200 OK` - Success

---

### 6. Delete Reviews

Delete all reviews from the database.

**Endpoint:** `DELETE /reviews`

**⚠️ Warning:** This action is irreversible!

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/reviews
```

**Response:**
```json
{
  "message": "All reviews deleted successfully",
  "deleted_count": 50
}
```

**Status Codes:**
- `200 OK` - Reviews deleted successfully

---

## Request/Response Formats

### Request Format

All POST requests must include:
- `Content-Type: application/json` header
- Valid JSON body

### Response Format

All responses are JSON with the following structure:

**Success Response:**
```json
{
  "data": {...},
  "status": "success"
}
```

**Error Response:**
```json
{
  "detail": "Error message here"
}
```

### Issue Object Structure

```json
{
  "severity": "critical|high|medium|low|info",
  "issue_type": "string",
  "message": "string",
  "line_number": 10,
  "suggestion": "string",
  "metadata": {
    "tool": "pylint|flake8|bandit|radon",
    "additional": "data"
  }
}
```

### Agent Result Structure

```json
{
  "agent_type": "quality|security|performance|documentation",
  "success": true,
  "execution_time": 2.5,
  "issues": [...],
  "error_message": null,
  "metadata": {
    "agent_type": "quality",
    "version": "1.0.0"
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Messages

**File Not Found:**
```json
{
  "detail": "File 'src/main.py' not found in repository."
}
```

**Repository Not Found:**
```json
{
  "detail": "Repository 'https://github.com/owner/repo' not found."
}
```

**GitHub Token Error:**
```json
{
  "detail": "GitHub token not configured. Please set GITHUB_TOKEN in .env file."
}
```

**Invalid Request:**
```json
{
  "detail": "Either file_path, commit_sha, pull_request_id, or scan_entire_repo must be provided."
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments, consider implementing:

- **Per IP:** 60 requests per minute
- **Per API Key:** 100 requests per minute

Rate limit headers (future):
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640000000
```

---

## Examples

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Create review
review_data = {
    "repository_url": "https://github.com/owner/repo",
    "file_path": "src/main.py"
}
response = requests.post(f"{BASE_URL}/reviews", json=review_data)
review = response.json()
print(f"Review ID: {review['review_id']}")
print(f"Total Issues: {review['total_issues']}")

# Get review details
review_id = review['review_id']
response = requests.get(f"{BASE_URL}/reviews/{review_id}")
details = response.json()

# List all reviews
response = requests.get(f"{BASE_URL}/reviews?limit=10")
reviews = response.json()

# Get analytics
response = requests.get(f"{BASE_URL}/reviews/analytics")
analytics = response.json()
print(f"Total Reviews: {analytics['total_reviews']}")
print(f"Total Issues: {analytics['total_issues']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

// Health check
async function healthCheck() {
  const response = await axios.get(`${BASE_URL}/health`);
  console.log(response.data);
}

// Create review
async function createReview() {
  const reviewData = {
    repository_url: 'https://github.com/owner/repo',
    file_path: 'src/main.py'
  };
  
  const response = await axios.post(`${BASE_URL}/reviews`, reviewData);
  console.log('Review ID:', response.data.review_id);
  console.log('Total Issues:', response.data.total_issues);
}

// Get analytics
async function getAnalytics() {
  const response = await axios.get(`${BASE_URL}/reviews/analytics`);
  console.log('Total Reviews:', response.data.total_reviews);
  console.log('Severity Stats:', response.data.severity_stats);
}
```

### cURL Examples

**Create Review:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/python/cpython",
    "file_path": "Lib/os.py"
  }'
```

**Get Review:**
```bash
curl http://localhost:8000/api/v1/reviews/1
```

**List Reviews:**
```bash
curl "http://localhost:8000/api/v1/reviews?limit=20&offset=0"
```

**Get Analytics:**
```bash
curl http://localhost:8000/api/v1/reviews/analytics
```

---

## Interactive API Documentation

When the API is running, you can access interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Try-it-out functionality
- Authentication testing

---

## Best Practices

### 1. Error Handling

Always check response status codes:

```python
response = requests.post(f"{BASE_URL}/reviews", json=data)
if response.status_code == 200:
    review = response.json()
else:
    error = response.json()
    print(f"Error: {error['detail']}")
```

### 2. Timeout Handling

Set appropriate timeouts for long-running operations:

```python
response = requests.post(
    f"{BASE_URL}/reviews",
    json=data,
    timeout=60  # 60 seconds
)
```

### 3. Retry Logic

Implement retry logic for transient failures:

```python
import time

def create_review_with_retry(data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{BASE_URL}/reviews", json=data)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 4. Pagination

Always use pagination for list endpoints:

```python
def get_all_reviews(limit=100):
    all_reviews = []
    offset = 0
    
    while True:
        response = requests.get(
            f"{BASE_URL}/reviews",
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        all_reviews.extend(data['reviews'])
        
        if len(data['reviews']) < limit:
            break
        offset += limit
    
    return all_reviews
```

---

## Versioning

Current API version: **v1**

Version is included in the base URL: `/api/v1`

Future versions will be available at `/api/v2`, `/api/v3`, etc.

---

## Support

For API support:
- Check interactive documentation: http://localhost:8000/docs
- Review error messages for specific issues
- Check server logs for detailed error information
- Contact: y.altunel@iku.edu.tr

---

**End of API Documentation**

*Last Updated: December 2025*  
*Version: 1.0.0*


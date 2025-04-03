# Cooking Assistant

A modern cooking Q&A application powered by AI that helps users with recipes, cooking techniques, ingredient substitutions, and kitchen tips.

## 🌟 Features

- **AI-Powered Cooking Assistance**: Get detailed answers to your cooking questions
- **Recipe Guidance**: Learn cooking techniques and ingredient substitutions
- **Reasoning Chain**: Understand the AI's thought process behind each answer
- **Modern UI**: Clean, responsive interface with dark theme
- **Docker Support**: Easy deployment with containerization
- **FastAPI Backend**: Fast and reliable API processing
- **Streamlit Frontend**: User-friendly interface

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone ai-cooking-assistant
cd ai-cooking-assistant
```

2. Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_api_key_here
```

3. Build and run the containers:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:8501
- Backend API docs: http://localhost:8000/docs

__________________________________________________________________________



POTENTIAL AWS DEPLOYMENT  

### Architecture Overview

- **ECS (Elastic Container Service)** for running Docker containers
- **Application Load Balancer** for traffic distribution
- **ECR (Elastic Container Registry)** for storing Docker images
- **Parameter Store** for securely storing the OpenAI API key
- **CloudWatch** for logging and monitoring

### Prerequisites

1. AWS CLI installed and configured
2. Docker installed locally
3. AWS account with necessary permissions

### Deployment Steps  ---> AI GENERATED 

1. **Create ECR Repositories**:
```bash
# Create repositories for both services
aws ecr create-repository --repository-name cooking-assistant-backend
aws ecr create-repository --repository-name cooking-assistant-frontend
```

2. **Store OpenAI API Key**:
```bash
# Store API key in Parameter Store
aws ssm put-parameter \
    --name "/cooking-assistant/prod/OPENAI_API_KEY" \
    --value "your-api-key" \
    --type "SecureString"
```

3. **Push Docker Images**:
```bash
# Login to ECR
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com

# Tag and push images
docker tag cooking-assistant-backend:latest your-account-id.dkr.ecr.your-region.amazonaws.com/cooking-assistant-backend:latest
docker tag cooking-assistant-frontend:latest your-account-id.dkr.ecr.your-region.amazonaws.com/cooking-assistant-frontend:latest

docker push your-account-id.dkr.ecr.your-region.amazonaws.com/cooking-assistant-backend:latest
docker push your-account-id.dkr.ecr.your-region.amazonaws.com/cooking-assistant-frontend:latest
```

4. **Create ECS Cluster**:
```bash
aws ecs create-cluster --cluster-name cooking-assistant-cluster
```

5. **Create Task Definitions**:
- Backend task definition with OpenAI API key from Parameter Store
- Frontend task definition with backend URL environment variable
- Configure appropriate CPU and memory limits
- Set up logging to CloudWatch

6. **Create Services**:
- Backend service behind Application Load Balancer
- Frontend service with public access
- Configure auto-scaling based on CPU/memory usage


### Monitoring and Maintenance

1. **CloudWatch Dashboards**:
- Container metrics
- API latency
- Error rates
- Cost metrics

2. **Alerts**:
- High CPU/memory usage
- API errors
- Cost thresholds
- OpenAI API quota

3. **Logging**:
- Container logs in CloudWatch
- Application logs with structured logging
- API access logs through ALB

4. **Backup and Disaster Recovery**:
- Regular ECR image backups
- Multi-region deployment option
- Automated rollback procedures

### Security Best Practices

1. **Network Security**:
- Use private subnets for backend containers
- Configure security groups properly
- Enable AWS WAF on ALB

2. **Access Control**:
- Use IAM roles for ECS tasks
- Implement least privilege principle
- Regular security audits

3. **Data Protection**:
- Encrypt data at rest and in transit
- Regular security patches
- API key rotation

### CI/CD Pipeline

1. **GitHub Actions Workflow**:
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
      - name: Build and push images
        run: |
          docker build -t backend .
          docker build -t frontend -f Dockerfile.streamlit .
          # Push to ECR
      - name: Deploy to ECS
        run: |
          aws ecs update-service --force-new-deployment
```


## 🛠️ Project Structure

```
.
├── app.py              # FastAPI backend application
├── cooking/
│   ├── __init__.py
│   ├── models.py       # Data models and validators
│   └── graph.py        # LangGraph workflow
├── streamlit_app.py    # Streamlit frontend application
├── Dockerfile          # Backend Dockerfile
├── Dockerfile.streamlit # Frontend Dockerfile
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Backend dependencies
└── requirements.streamlit.txt  # Frontend dependencies
```

## 🐳 Docker Configuration

The project uses Docker Compose to run both frontend and backend services:

### Backend Service
- Python 3.11 base image
- FastAPI application
- Exposed on port 8000
- Includes LangChain and OpenAI integration

### Frontend Service
- Python 3.11 base image
- Streamlit application
- Exposed on port 8501
- Dark theme UI

## 🔧 Development

### Running Locally

1. Start the services:
```bash
docker-compose up
```

2. Stop the services:
```bash
docker-compose down
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuilding After Changes

```bash
docker-compose up --build
```

## 🌐 API Endpoints

### `/cooking/query`
- **Method**: POST
- **Purpose**: Submit cooking-related questions
- **Request Body**:
  ```json
  {
    "query": "How do I make pasta?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "Detailed cooking instructions...",
    "reasoning_chain": ["Step 1...", "Step 2..."]
  }
  ```

## 🎨 Frontend Features

- Dark theme UI
- Real-time query processing
- Expandable reasoning chain
- Error handling and feedback
- Debug information panel
- Responsive design

## ⚙️ Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `BACKEND_URL`: Backend service URL (default: http://localhost:8000)

## 🔒 Security Notes

- Never commit your `.env` file
- Keep your OpenAI API key secure
- Use appropriate firewall rules in production
______________________________________________________________


## 🔒 Enhancing tthe application with security 

### Authentication & Authorization

1. **JWT Authentication (Token Authentication)**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

# JWT configuration
SECRET_KEY = "your-secret-key"  # Store in Parameter Store for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

# Protected endpoint example
@app.post("/cooking/query")
async def query_endpoint(
    query: CookingQuery,
    current_user: str = Depends(get_current_user)
):
    # Process query...
```

2. **Rate Limiting To Avoid Overload/Costs And Bots**:
```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/cooking/query")
@limiter.limit("5/minute")  # Adjust limits as needed
async def rate_limited_endpoint(request: Request):
    # Process request...
```

### API Key Security

1. **Environment Variables --> KEEP VARIABLES IN .env ALWAYS and fetch them from AWS parameter store**:
- Development:
  ```bash
  # .env
  OPENAI_API_KEY=sk-...
  JWT_SECRET_KEY=...
  ```

- Production (AWS Parameter Store):
  ```bash
  # Fetch secrets in app startup
  import boto3
  
  ssm = boto3.client('ssm')
  response = ssm.get_parameter(
      Name='/cooking-assistant/prod/OPENAI_API_KEY',
      WithDecryption=True
  )
  OPENAI_API_KEY = response['Parameter']['Value']
  ```

2. **Key Rotation --> CHANGE API KEY TO AVOID EXPOSED API KEYS OR LEAKAGE**:
```python
from datetime import datetime, timedelta

def should_rotate_key(last_rotation: datetime) -> bool:
    return datetime.now() - last_rotation > timedelta(days=30)

def rotate_api_key():
    # Implement key rotation logic
    pass
```

### Endpoint Security

1. **CORS Configuration--> RESTRICT INCOMING CALLS ONLY FROM FRONTEND**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Request Validation---> AVOID UNNECESSARY API CALLS WITH BS QUERIES**:
```python
from pydantic import BaseModel, Field

class SecureQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(..., regex="^[a-zA-Z0-9-]+$")
```

3. **SSL/TLS Configuration---> MUST HAVE**:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
```

### Security Best Practices

1. **Input Sanitization**:
- Validate all input parameters
- Use Pydantic models for request validation
- Implement content security policies --> OpenAI moderation API or python Guardrails 

2. **Logging and Monitoring**:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/cooking/query")
async def logged_endpoint(query: SecureQuery):
    logger.info(f"Request received from user {query.user_id}")
    # Process query...
```

3. **Error Handling**:
```python
from fastapi import HTTPException

@app.exception_handler(HTTPException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": request.state.request_id
        }
    )
```

4. **Security Headers Through MiddleWare**:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```


### Production Security Checklist REQUESTED FOR SOC 2 IMPLEMENTATIONS AND AUDITS

1. **Infrastructure**:
- Use AWS WAF for additional protection
- Enable AWS Shield for DDoS protection
- Implement VPC endpoints for AWS services

2. **Monitoring**:
- Set up CloudWatch alerts for suspicious activities
- Monitor failed authentication attempts
- Track API usage patterns

3. **Compliance**:
- Implement audit logging
- Set up automated security scanning
- Regular penetration testing

🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖BUILT WITH EXCITEMENT FOR PRESSW TEAM   🤖🤖🤖🤖🤖🤖🤖🤖
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖ALEX LOUIZOS🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖

## 🔍 Edge Cases and Limitations

### Query Edge Cases

1. **Multi-Language Queries**:
- Non-English recipe requests
- Mixed language ingredients
- Regional cooking terms
- NLP models might be able to reply in the language of choice but their tokenization suffers so it is
  better to translation in english 
```python
# Example handling in models.py
class CookingQuery(BaseModel):
    query: str
    language: str = Field(default="en", pattern="^[a-z]{2}$")
    
    @validator('query')
    def validate_query_language(cls, v, values):
        if values.get('language') != "en":
            # Translate query to English before processing
            # Translate response back to requested language
            pass
        return v
```

2. **Dietary Restrictions and Allergies**:
- Multiple conflicting restrictions
- Uncommon allergies
- Religious dietary laws
```python
class DietaryRestrictions(BaseModel):
    allergies: List[str] = []
    dietary_type: Optional[str] = None  # vegan, kosher, halal, etc.
    restrictions: List[str] = []
    severity_level: str = "normal"  # normal, strict, medical
```

3. **Measurement Conversions**:
- Mixed metric/imperial units
- Regional measurement variations
- Non-standard measurements ("pinch", "handful")
```python
def normalize_measurements(ingredients: List[Dict]):
    for ingredient in ingredients:
        if "amount" in ingredient and "unit" in ingredient:
            # Convert to standard units
            ingredient["standardized"] = convert_to_standard_unit(
                ingredient["amount"],
                ingredient["unit"]
            )
```

### Content Safety

1. **Unsafe Cooking Instructions**:
- Dangerous cooking techniques
- Raw food safety concerns
- High-risk ingredients
```python
def safety_check(instructions: List[str]) -> bool:
    unsafe_patterns = [
        "raw eggs",
        "extremely high heat",
        "pressure cooker without safety",
        # ... more patterns
    ]
    return validate_safety(instructions, unsafe_patterns)
```

2. **Equipment Safety**:
- Uncommon kitchen tools
- Professional equipment in home settings
- Alternative tool suggestions
```python
class EquipmentValidator:
    def validate_equipment(self, required_equipment: List[str]) -> Dict:
        return {
            "safe_for_home": self.check_home_safety(required_equipment),
            "alternatives": self.suggest_alternatives(required_equipment),
            "warnings": self.get_safety_warnings(required_equipment)
        }
```

### Input Validation

1. **Query Length and Complexity**:
- Extremely long recipes
- Multi-part cooking questions
- Follow-up questions
```python
class QueryValidator:
    MAX_QUERY_LENGTH = 1000
    MAX_STEPS = 20
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        if len(query) > self.MAX_QUERY_LENGTH:
            return False, "Query too long"
        if self.count_questions(query) > 3:
            return False, "Too many questions in one query"
        return True, ""
```

2. **Ingredient Validation**:
- Non-existent ingredients
- Seasonal availability
- Regional availability
```python
class IngredientValidator:
    def validate_ingredients(self, ingredients: List[str]) -> Dict:
        return {
            "available": self.check_availability(ingredients),
            "seasonal": self.check_seasonality(ingredients),
            "substitutes": self.find_substitutes(ingredients)
        }
```

### Error Handling

1. **API Failures**:
- OpenAI API rate limits
- Network timeouts
- Partial responses
```python
async def handle_llm_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except OpenAIError as e:
            if "rate_limit" in str(e):
                return get_cached_response() or get_fallback_response()
            raise
        except TimeoutError:
            return get_simple_response()
    return wrapper
```

2. **Response Quality**:
- Incomplete recipes
- Unclear instructions
- Missing ingredients
```python
class ResponseValidator:
    def validate_recipe_response(self, response: Dict) -> Dict:
        checks = {
            "has_ingredients": bool(response.get("ingredients")),
            "has_steps": bool(response.get("steps")),
            "has_timing": any("minutes" in step or "hours" in step 
                            for step in response.get("steps", [])),
            "has_temperatures": self.check_temperature_info(response)
        }
        if not all(checks.values()):
            return self.enhance_response(response, checks)
        return response
```
#   a i - c o o k i n g - a g e n t 
 
 

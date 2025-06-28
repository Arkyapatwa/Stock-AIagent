# Stock Market AI Agents

This project implements a multi-agent system for stock market analysis and signal prediction. It leverages various AI agents to perform fundamental analysis, technical analysis, and ultimately predict stock signals.

## Getting Started

Follow these instructions to set up and run the application.

### Prerequisites

- Python 3.12
- pip (Python package installer)
- Docker (optional, for containerized deployment)

### Installation (without Docker)

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Arkyapatwa/Stock-AIagent.git
    cd Stock-AIagent
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the root directory based on `.env.example` and fill in your API keys and other configurations.

    ```
    # Example .env content
    GITHUB_TOKEN=your_github_token
    MODEL_ENDPOINT=your_model_endpoint
    LLM_MODEL=your_llm_model
    ```

5.  **Run the application:**

    ```bash
    uvicorn main:app --reload --port 8000
    ```

    The application will be accessible at `http://localhost:8000`.

### Installation (with Docker)

1.  **Build the Docker image:**

    Navigate to the root directory of the project where the `Dockerfile` is located, then run:

    ```bash
    docker build -t stock-market-app .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -p 8000:8000 stock-market-app
    ```

    The application will be accessible at `http://localhost:8000`.

## Project Structure

-   `main.py`: The main FastAPI application entry point.
-   `agents/`: Contains the different AI agents (e.g., fundamental, technical, prediction, supervisor).
-   `tools/`: Houses the tools used by the agents for data retrieval and analysis.
-   `models/`: Defines data models and agent states.
-   `utils/`: Utility functions and common components.
-   `requirements.txt`: Python dependencies.
-   `Dockerfile`: Docker containerization configuration.

## API Endpoints

-   `/predict_signal`: Endpoint for predicting stock signals.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.
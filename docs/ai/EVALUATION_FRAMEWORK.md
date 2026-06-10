# Evaluation Framework

The Evaluation Framework is an automated testing harness for stochastic AI models (LLM-as-a-Judge).

## Core Concepts
*   **Golden Dataset:** A verified collection of `DatasetRow` objects containing an `input_payload` and the `expected_output`.
*   **LLM Judge:** A highly capable model (e.g., GPT-4o) tasked with grading another model's output based on a predefined rubric.

## Execution Flow
1.  A developer triggers an evaluation via `POST /api/v1/evaluations/run`.
2.  The FastAPI router creates an `EvaluationJob` in the database and spawns a `BackgroundTask`.
3.  The worker iterates over the dataset.
4.  For each row, it invokes the *Target Prompt* using the target model.
5.  It then invokes the *Judge Prompt* using the Judge model, providing the Target Output and the Expected Output.
6.  The Judge returns a normalized score (`0.0` to `1.0`).

## Evaluation Metrics
*   **Semantic Similarity:** Does the output mean the same thing as the expected output, despite differing syntax?
*   **Formatting:** Did the model return valid JSON?
*   **Safety:** Did the model exhibit bias or leak internal instructions?

## Scalability Gap
**(CRITICAL):** The framework relies on `fastapi.BackgroundTasks`. This executes in the same memory space as the API worker. If the pod scales down or crashes, all pending evaluations are lost forever.
**Migration Required:** Move execution logic to Celery workers listening to a Redis broker.

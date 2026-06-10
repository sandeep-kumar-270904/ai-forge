# Prompt Architecture

Prompt engineering in AIForge is treated with the same rigor as software engineering. Prompts are immutable code artifacts.

## Maker / Checker Workflow
To prevent "Prompt Drift", developers cannot edit a live prompt.
1.  **Maker:** An AI Engineer creates a new `PromptVersion` containing the system instruction string and expected variables.
2.  **Checker:** A Lead Engineer reviews the version and links it to a `PromptDeployment`.
3.  **Live:** The API endpoint `GET /prompts/{name}/live` fetches the active deployment.

## Variable Substitution
AIForge uses f-string style template substitution (`{variable_name}`).
The `expected_variables` JSONB column enforces strict validation. If the `SwarmExecutor` attempts to invoke a prompt but fails to provide all expected variables, a `422 Unprocessable Entity` is raised *before* invoking the LLM.

## Hallucination Mitigation Strategy
Prompts must adhere to strict schemas. For Supervisor nodes, the prompt mandates outputting *only* the name of the next agent or the word `FINISH`. (Note: Transitioning to OpenAI Structured Outputs / JSON Schema is planned for Phase 3).

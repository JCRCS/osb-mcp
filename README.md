# OSB-MCP (Open Study Builder - Model Context Protocol)

## Overview

OSB-MCP is a multi-agent system that automates the StudyBuilder creation process using Google ADK (Agent Development Kit) agents. The system consists of multiple specialized agents working together to search for information and create StudyBuilder objects in a specified order.

## System Components

1. **Google Search Agent**: This agent queries Google to gather necessary information for StudyBuilder creation.
2. **Order Verification Agent**: This agent validates and ensures that StudyBuilder objects are created in the correct sequential order.

## Prerequisites

- Python 3.8 or higher
- Google ADK (Agent Development Kit)
- Google API credentials for search functionality
- Required Python packages (see `requirements.txt`)

## 🔐 Environment Setup

1. Copy `.env.example` to `.env`.
2. Fill in your API keys and configuration values.
3. Ensure that `.env` is not committed to version control.

```bash
cp .env.example .env
```

# [EXECUTE] Ready to step aside and let the Pythonic uv way handle it for you?
```bash
uv venv
source .venv/bin/activate
uv sync
uv run adk web # (wait for 30 seconds)
```


# [EXECUTE] Do you want to go all-in with pip instead?
```bash
pip install google-adk google-generativeai mcp python-dotenv nest_asyncio litellm serpapi google-search-results markdown bs4
```

## StudyBuilder Creation Process

The system follows a specific order when creating StudyBuilder objects. The Order Verification Agent ensures that each step is completed before proceeding to the next:

1. Initial information gathering via Google Search Agent
2. Validation of gathered information
3. Sequential creation of StudyBuilder components based on the defined order
4. Final verification and output generation

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify your Google API credentials are correct and have the necessary permissions
3. Ensure all required dependencies are installed


# Already cooked prompting
## 🔍 Search on the Internet

**Objective**: Gather background information to inform the study design.

> **Prompt**  
> _Search for key concepts related to clinical trials for Crohn’s disease, including:_  
> - Trial structure  
> - Study groups  
> - Phases and epochs  
> - Titration of medications  
> - Activity scheduling  
>   
> Use this information to guide the creation of a realistic and compliant clinical trial model.

---

## 🏗️ Build the Clinical Trial – First, Plan It

### 🧪 Basic Study Design

> **Prompt**  
> Create a simple sample study for Crohn’s disease. Include:  
> - 2 Arms  
> - 2 Epochs  
> - Study Elements  
> - Design Cells  
>   
> Provide a complete proposal filling all properties accordingly.

---

### 🧪 Advanced Study Design

> **Prompt**  
> Design a more complex clinical trial for Crohn’s disease. Include:  
> - 5 Arms  
> - 5 Epochs  
> - 5 Elements  
> - Corresponding Design Cells  
>   
> Provide a comprehensive structure with all fields populated.

---

## 📅 Define the Schedule and Activities

### 📆 Study Visit Activity Schedule

> **Prompt**  
>Create a new study and detailed visit and activity schedule.
>Suggest and justify appropriate input data for:
>
>Visit timing
>Visit frequency
>Associated activities
>
>do what is needed to create it, do your best suggestion to set the properties

---

### ✅ Define Study Activities

> **Prompt**  
> Create a study activity configuration for `Study_000002`.  
> Suggest the input parameters including:  
> - Activity name  
> - Description  
> - Timing  
> - Assigned roles

---



# UPGRADE libraries

```bash
# remove venv
# remove toml
uv init
uv venv
uv pip install google-adk google-generativeai mcp python-dotenv nest_asyncio litellm serpapi google-search-results markdown bs4
uv pip freeze > requirements.txt
uv add -r requirements.txt
uv sync
uv lock
```

## License

[License information here]

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

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/osb-mcp.git
   cd osb-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the required APIs (Search, etc.)
   - Create API credentials and save them as `credentials.json` in the project root

## Configuration

Configure the system by editing the `config.json` file with your specific parameters:

```json
{
  "google_api_key": "YOUR_API_KEY",
  "search_parameters": {
    "max_results": 10,
    "search_depth": 2
  },
  "studybuilder": {
    "creation_order": ["component1", "component2", "component3"]
  }
}
```

## Running the System

1. Start the main application:
   ```bash
   python main.py
   ```

2. Monitor the agent activity:
   ```bash
   python monitor.py
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

## License

[License information here]

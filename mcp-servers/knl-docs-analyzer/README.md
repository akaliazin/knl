# KNL Documentation Analyzer MCP Server

Mock MCP server for AI-powered documentation analysis.

## Overview

This server provides tools for analyzing code changes and generating documentation update proposals. Currently implemented as a stub with hardcoded responses to demonstrate the workflow.

## Tools

### `analyze_doc_gaps`
Analyzes code changes and identifies documentation gaps.

**Input:**
- `task_id`: Task ID to analyze
- `context`: Documentation context from DocAnalyzer

**Output:** DocUpdateProposal JSON

### `generate_doc_updates`
Generates specific documentation update proposals.

**Input:**
- `task_id`: Task ID
- `context`: Analysis context
- `gaps`: Identified documentation gaps

**Output:** DocUpdateProposal JSON

## Resources

- `knl://task/context` - Task context and metadata
- `knl://changes` - Git commits and diffs
- `knl://docs` - Current documentation files

## Usage

The server is automatically started by the KNL CLI when running `knl docs update`.

## Implementation Status

**Current:** Mock/stub implementation with hardcoded responses
**Future:** Real AI analysis using Claude API

## Running Standalone

```bash
# Install dependencies
cd mcp-servers/knl-docs-analyzer
uv pip install -e .

# Run server
python -m knl_docs_analyzer.server
```

## Upgrading to Real AI

To upgrade this stub to use real AI analysis:

1. Add Claude API integration in `server.py`
2. Replace `create_mock_proposal()` with real analysis
3. Add proper context processing and prompt engineering
4. Implement error handling and retries
5. Add response validation

See task context (#1) for detailed upgrade plan.

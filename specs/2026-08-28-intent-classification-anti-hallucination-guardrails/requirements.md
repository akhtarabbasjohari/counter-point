# Phase 9 Specification: Dynamic Query Intent Classification & Zero-Hallucination Guardrails

## Scope
Phase 9 eliminates model output hallucination and rigid template responses for simple words, greetings, or off-topic queries. It equips the CounterPoint agent with dynamic intent classification, adaptive response formatting, and strict zero-hallucination guardrails across both online (Groq LLM) and offline (rule-based fallback) execution paths.

## Background & Problem Statement
Currently, CounterPoint forces every input query (e.g., "hi", "hello", "what is this?", "how are you?") through a single rigid 4-section competitive synthesis template. This causes:
1. **Unnecessary External Tool Execution**: Launching web searches for greetings or generic words.
2. **Model & Fallback Hallucinations**: Inventing fake pricing tables (e.g. `$5-$15/mo`), arbitrary benchmarks, and dummy competitor entries for non-competitor or off-topic queries.
3. **Rigid Formatting Over-application**: Returning strategic matrices, gap analysis, and tactical recommendations when the user only expects a direct conversational answer or product introduction.

To solve this, CounterPoint requires:
- **Query Intent Classifier**: Categorizing user prompts into `GREETING`, `OFF_TOPIC`, `GENERAL_QA`, or `COMPETITOR_RESEARCH`.
- **Conditional Workflow Routing**: Bypassing web search and matrix synthesis for non-research prompts.
- **Adaptive Synthesis System Prompt**: Structuring LLM responses flexibly according to intent.
- **Strict Anti-Hallucination Policy**: Eliminating all synthetic pricing assumptions and instructing models to report missing data explicitly ("No pricing information available in retrieved web search sources").

## Key Requirements

### 1. Intent Classification Engine
- Implement an explicit query intent classification mechanism in `LangGraphEngine` and `QueryRewriter`.
- Supported Intent Categories:
  - `GREETING`: Phrases like "hi", "hello", "hey", "good morning".
  - `OFF_TOPIC`: Queries unrelated to competitive intelligence or business software positioning (e.g., "what is the capital of France?", "tell me a joke").
  - `GENERAL_QA`: Queries asking about CounterPoint's capabilities or how to use the dashboard (e.g., "what can you do?", "how do I upload a document?").
  - `COMPETITOR_RESEARCH`: Queries inquiring about software products, competitors, pricing, market trends, or positioning document analysis (e.g., "compare Salesforce vs HubSpot pricing", "analyze Notion positioning").

### 2. Conditional Graph Routing in LangGraph
- Update `AgentMemoryState` to store `intent: str` (e.g. `GREETING`, `OFF_TOPIC`, `GENERAL_QA`, `COMPETITOR_RESEARCH`).
- Update `_query_analysis_node` to classify query intent.
- In `_web_research_node`: Only execute live web search if `intent == 'COMPETITOR_RESEARCH'`.
- In `_strategy_synthesis_node` / `GroqReasoningEngine`:
  - For `GREETING`: Respond concisely with a welcoming greeting and a brief introduction to CounterPoint's competitive research capabilities.
  - For `GENERAL_QA`: Provide clear instructions on how to use CounterPoint (e.g., uploading PDF/TXT strategy files, asking competitor questions).
  - For `OFF_TOPIC`: Politely state that CounterPoint specializes in competitive intelligence and strategic positioning analysis, offering to assist with competitor research.
  - For `COMPETITOR_RESEARCH`: Execute full competitive analysis synthesis with section headers and tables, but strictly anchored to authentic web and document data.

### 3. Zero-Hallucination Guardrails
- **Remove Fake Fallback Data**: Remove static synthetic pricing tables (`| Entry Pricing | Self-serve low tier ($5-$15/mo) |`) in `GroqReasoningEngine._generate_fallback_synthesis`.
- **Honest Data Gaps**: If web search returns 0 results or pricing details are not found in snippets, explicit text must state: *"No verified external pricing data found in search results for [Query]"*.
- **Citing Sources**: Ensure every table entry or claims in section 2/3 reflect verified snippets or document content.

### 4. Direct API & Fallback Engine Alignment
- Ensure `GroqReasoningEngine.synthesize_counterpoint` respects the determined intent even when falling back to rule-based synthesis.
- Ensure `LangGraphEngine.execute_graph_synthesis` passes `intent` through state checkpoints and returns accurate audit logs.

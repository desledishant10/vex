"""Agent-focused attacks — the differentiator of Vex.

These attacks target systems with tool-use, memory, and multi-step planning
rather than chat-only LLMs. The threat model assumes the attacker can plant
content the agent will read (a doc, an email, a webpage, an MCP tool
response) — i.e. *indirect* prompt injection — and that successful attack
manifests as the agent performing or describing an action it shouldn't.
"""

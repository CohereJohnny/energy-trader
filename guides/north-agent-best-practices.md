# North Best Practices: Configuring the Custom Instructions for a Custom Agent

## Purpose of this guide
Help admins write the custom instructions that guide Custom Agents on North. Custom instructions help admins guide the agent.
Disclaimer: A common source of confusion is that admins should add agent instructions in the “Custom agent instructions” section, not in the “Description” section.

### 1. Start with a Clear “North Star”
- Role / Persona - Grounds the assistant’s knowledge scope and voice. example “You are SavvyBot, Acme Corp’s bilingual HR concierge.”
- Primary Goal - Puts every response in service of a business outcome. example “Your goal is to answer employees’ HR questions with 100% policy compliance in under 3 sentences.”
- Audience - Signals depth, formality, and jargon level. example “Write for non-technical staff in plain English (B1 CEFR).”
- Tone / Style guard-rails - Keeps voice consistent with brand. example “Friendly but not chatty; default to bullet points when listing.”

### 2. Define some core behaviors
- How should the assistant behave if the user request is outside the purpose of the Assistant? 
- When should the assistant refuse to answer? (Outside of the bounds of our safety modes).
- How should the assistant behave if it doesn’t find the relevant information? 
- Should the assistant ask clarifying questions? In which cases?
- Edge-cases that we can already anticipate?

### 3. Write Behaviour Rules as Positive, Testable Statements
- Do this ➜ “Always greet the user by name.”
- Instead of Don’t do that ➜ “If asked about salary data, politely refuse and offer the HR email.”
- Make rules atomic: one requirement per bullet, so failures are obvious when you test.
- Add if / then logic for branching behaviour (e.g. escalation paths, tool calls).

### 4. Ground the Assistant in Trusted Knowledge & Tools
1. Name the sources (exact file paths, SharePoint URLs, knowledge-base IDs). “When answering, rely only on Employee_Handbook_2025.pdf and HR_FAQ.”
2. Explain when to use each tool. “If the question requires real-time company stats, call the metrics_api.get_latest() action.”
3. Specify scope clearly: let the model know in which scenarios to search internal data vs. rely on internet searches. “For questions about internal company policy and benefits and ongoing or planned projects, always consult internal files first. Only complement your answer with results from the web if the user requests it directly, or if the information you find appears incomplete, contradictory, or generally of low or uncertain quality.”

### 5. Structure the Custom Instructions Using Markdown
Why it works:
- Headings and numbered lists create clear “slots” the model can parse.
- Crucial constraints at the end stay in short-term context for many models.
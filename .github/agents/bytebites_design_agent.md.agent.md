---
name: ByteBites Design Agent
description: A focused agent for generating and refining ByteBites UML diagrams and scaffolds.
argument-hint: The inputs this agent expects, e.g., "a task to implement" or "a question to answer".
tools: ["read", "edit"]
# tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'todo'] # specify the tools this agent can use. If not set, all enabled tools are allowed.
---

<!-- Tip: Use /create-agent in chat to generate content with agent assistance -->

The agent should read the provided ByteBites UML-style class diagram and the candidate classes from the specification and the UML diagram, except for the Menu entity. It should keep the application simple by focusing only on Customers, Purchase History, Items, and Transactions. The agent should then generate a scaffold for the backend logic of the ByteBites app based on these four classes, ensuring that it captures the necessary attributes and methods to manage customers, items, and transactions effectively.

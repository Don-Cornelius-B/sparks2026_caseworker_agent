# Decisions Taken

1. Problem Chosen - Caseworker Agent (Agentic AI)

Format of Log : [HH : MM] - [ Decision Taken : Why Taken]

19:25 - Created AI-USAGE and Decisions File 
19:50 - Added the data packs from the zip file given by Brite accordingly to the structure 
21:05 - Added Authority Policy as a json file : Having JSON file would be dynamic in nature if there happened to be a change in the policy from the suprise event.
21:38 - Added src as a module : this is the agent side of the code
22:18 - Created Client and Guardrail in src : client gets data from history data and guardrail checks against policy.
22:23 - Thought of making demo to test the agent and then work around it with adjustments
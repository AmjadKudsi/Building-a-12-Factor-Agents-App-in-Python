=== Launching agent ===
Launched agent with ID: 75128e6a-8695-4c99-9d2d-b95437e70e3d
Initial status: running

=== Pausing agent ===
Pause response status code: 200
Status: paused | Steps: 0
Confirmed status after pause: paused

=== Resuming agent ===
Resume response status code: 200
Resumed agent. Status: running

=== Attempting duplicate resume (expect 409) ===
Status code: 409
Response body: {'detail': 'Agent is already running'}
Correct! Duplicate resume blocked with 409 Conflict.

=== Polling for completion ===
Poll 1: status=running | steps=0
Poll 2: status=running | steps=0
Poll 3: status=running | steps=0
Poll 4: status=running | steps=0
Poll 5: status=running | steps=0
Poll 6: status=running | steps=0
Poll 7: status=running | steps=0
Poll 8: status=running | steps=0
Poll 9: status=running | steps=1
Poll 10: status=running | steps=1
Poll 11: status=running | steps=1
Poll 12: status=running | steps=1
Poll 13: status=running | steps=2
Poll 14: status=running | steps=2
Poll 15: status=running | steps=2
Poll 16: status=running | steps=2
Poll 17: status=running | steps=2
Poll 18: status=running | steps=2
Poll 19: status=running | steps=3
Poll 20: status=running | steps=3
Poll 21: status=running | steps=3
Poll 22: status=complete | steps=5

Final status: complete
Final answer: The solutions are x = 2 and x = 3 (since x^2 − 5x + 6 factors as (x − 2)(x − 3) = 0).

=== Attempting to resume non-existent agent (expect 404) ===
Status code: 404
Response body: {'detail': 'State not found'}
Correct! Non-existent agent returns 404.
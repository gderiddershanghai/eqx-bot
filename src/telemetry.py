# import time
# import json
# import logging
# from dataclasses import dataclass, asdict
# from typing import Dict, Any

# # 1. Configure structured logging
# # We log to a file so you can inspect it later (rag_metrics.jsonl)
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(message)s',
#     handlers=[
#         logging.FileHandler("rag_metrics.jsonl"), # Logs to file
#         # logging.StreamHandler() # Uncomment to see logs in console too
#     ]
# )

# logger = logging.getLogger("EQxTelemetry")

# @dataclass
# class RAGEvent:
#     event_type: str        # e.g., "retrieval", "generation", "router_classification"
#     query: str
#     latency_ms: float
#     metadata: Dict[str, Any]
#     timestamp: float = time.time()

# class Telemetry:
#     def log_event(self, event_type: str, query: str, start_time: float, metadata: Dict[str, Any] = {}):
#         """
#         Logs a structured event to the jsonl file.
        
#         Args:
#             event_type: Category of the event.
#             query: The user's input string.
#             start_time: The time.time() when the operation started.
#             metadata: Any extra dict of data (tokens, model name, filters).
#         """
#         # Calculate how long the operation took
#         latency = (time.time() - start_time) * 1000
        
#         # Create the event object
#         event = RAGEvent(
#             event_type=event_type,
#             query=query,
#             latency_ms=round(latency, 2),
#             metadata=metadata
#         )
        
#         # Write as a JSON line
#         logger.info(json.dumps(asdict(event)))

# # Singleton instance - This is what other files import
# telemetry = Telemetry()
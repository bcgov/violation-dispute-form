#!/usr/bin/env bash
curl -X POST \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --output "output.pdf" \
  -d '@test-data-notice-in-person.json' \
  "http://localhost:8000/api/v1/submit-form/?name=notice-to-disputant-response"

  # "http://localhost:8081/form/?name=notice-to-disputant-response"

  # "http://0.0.0.0:8081/form/?name=violation-ticket-statement-and-written-reasons"

  # "http://localhost:8000/form/?name=violation-ticket-statement-and-written-reasons"


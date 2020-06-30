#!/usr/bin/env bash
curl -X POST --output notice-to-disputant-response.pdf \
  -H 'Accept: application/pdf' \
  -H 'Content-Type: application/json' \
  -d '@test-data-notice-in-person.json' \
  "http://localhost:8081/form/?name=notice-to-disputant-response"

  # "http://0.0.0.0:8081/form/?name=violation-ticket-statement-and-written-reasons"

  # "http://localhost:8000/form/?name=violation-ticket-statement-and-written-reasons"


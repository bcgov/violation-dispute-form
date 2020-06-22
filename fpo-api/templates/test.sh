#!/usr/bin/env bash
curl -X POST --output violation-ticket-statement-and-written-reasons.pdf \
  -H 'Accept: application/pdf' \
  -H 'Content-Type: application/json' \
  -d '@./test-data-violation.json' \
  "http://localhost:8081/form?name=violation-ticket-statement-and-written-reasons"
  # "http://localhost:8081/form/?name=notice-to-disputant-response"

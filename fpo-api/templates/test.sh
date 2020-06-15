#!/usr/bin/env bash
  curl -X POST --output output.pdf \
    -H 'Accept: application/pdf' \
    -H 'Content-Type: application/json' \
    -d '@test-data.json' \
    "http://localhost:8000/form?name=notice-to-disputant-response"
    # "http://localhost:8081/form?name=violation-ticket-statement-and-written-reasons"

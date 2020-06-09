curl -X POST --output violation-ticket-statement-and-written-reasons.pdf \
  -H 'Accept: application/pdf' \
  -H 'Content-Type: text/html' \
  -d '@violation-ticket-statement-and-written-reasons.html' \
  http://localhost:8083/pdf?filename=violation-ticket-statement-and-written-reasons.pdf


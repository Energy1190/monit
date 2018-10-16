#!/usr/bin/env sh

URL=${SEND_URL}
NAME=${SEND_NAME}
DESCRIPTION=${DESCRIPTION}

PAYLOAD="{
  \"attachments\": [
    {
      \"title\": \"With $NAME something is wrong.\",
      \"color\": \"warning\",
      \"mrkdwn_in\": [\"text\"],
      \"fields\": [
        { \"title\": \"Date\", \"value\": \"$MONIT_DATE\", \"short\": true },
        { \"title\": \"Host\", \"value\": \"$MONIT_HOST\", \"short\": true },
		{ \"title\": \"Description\", \"value\": \"$DESCRIPTION\", \"short\": true }
      ]
    }
  ]
}"

curl -s -X POST --data-urlencode "payload=$PAYLOAD" $URL
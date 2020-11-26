# torivahti-agent

## Torivahti
Torivahti is a hobby project to create a Telegram bot that notifies the user if new items matching their query are posted in tori.fi marketplace.

Torivahti-agent is the backend agent which runs on a schedule in AWS Lambda, searching tori.fi for new items. Data for the queries is stored in DynamoDB. Both the chatbot and the backend agent can send messages to the user.

Torivahti "frontend" (chatbot) code can be found here: https://github.com/ttalikka/torivahti

## TODO
* Database updating when new items are found
* Better user experience

### DynamoDB schema
* id: Unique ID for the entry
* chat: Telegram chat ID (which user to respond to)
* latest: The most recent item found in tori.fi that was shown to the user
* searchQuery: URL-encoded search query used in tori.fi
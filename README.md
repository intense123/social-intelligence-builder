# Social Intelligence Builder

An OMI Memory Trigger integration that extracts social intelligence data from conversation memories. This Flask app processes memory trigger events from OMI, extracts relationship insights using GPT-4o, and visualizes them in a beautiful dashboard.

## Features

- **Social Intelligence Extraction**
  - People mentioned in conversations
  - Locations discussed
  - Emotions expressed
  - Social intent (e.g., bonding, arguing, reconnecting)

- **Visual Dashboard**
  - Beautiful web interface to view all insights
  - Emoji reactions based on emotions (😄 for happy, 😬 for awkward, etc.)
  - Important memories highlighted with 🔥
  - Statistics about your social interactions

- **OMI Integration**
  - Webhook for memory trigger events
  - Setup status endpoint
  - Dashboard link included in responses

## Dashboard Screenshots

### Main Dashboard View
![Dashboard Overview](screenshots/dashboard_overview.png)

The dashboard provides a comprehensive view of all your social insights, including people, locations, emotions, and social intent.

### Important Memories
![Important Memories](screenshots/important_memories.png)

Important memories are highlighted with a 🔥 icon and yellow background, making them easy to spot.

### Emoji Reactions
![Emoji Reactions](screenshots/emoji_reactions.png)

Each memory includes an emoji reaction based on the detected emotions, adding personality to your social insights.

## Setup

1. Clone this repository
   ```
   git clone <repository-url>
   cd social-intelligence-builder
   ```

2. Create a virtual environment and install dependencies
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key
   ```
   # Create a .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

## Running the App

Start the Flask server:
```
python app.py
```

For public access (development only):
```
# Install ngrok if you haven't already
brew install ngrok  # On macOS
# or download from https://ngrok.com/download

# Run ngrok to expose your local server
ngrok http 5001
```

## Endpoints

### GET /dashboard

The visual dashboard for viewing all social intelligence insights.

**Access**: Open in any web browser
```
http://localhost:5001/dashboard
```

### POST /memory-trigger

Receives memory data from OMI and extracts social intelligence.

**Request**: Memory data in the format provided by OMI.

**Response**:
```json
{
  "status": "ok",
  "extracted": {
    "people": ["Sarah"],
    "locations": ["Coffee Shop", "Brooklyn"],
    "emotions": ["excited"],
    "social_intent": "reconnect",
    "uid": "user123"
  },
  "summary": "📊 Social Intelligence: People: Sarah | Location: Coffee Shop, Brooklyn | Emotions: excited | Intent: reconnect | 🔥 Key insight: Rekindling friendship shows mutual interest in staying connected."
}
```

### GET /setup-status

Returns the setup status of the app.

**Response**:
```json
{
  "is_setup_completed": true
}
```

## Data Storage

Insights are stored in `data/people.json` with:
- Structured data (people, locations, emotions, intent)
- Human-readable summary
- Timestamp
- User ID

## Integration with OMI

1. Deploy this app or use ngrok to get a public URL
2. In OMI:
   - Go to Settings > Developer Mode > Developer Settings
   - Set Memory Creation Webhook URL to: `https://your-url.com/memory-trigger`
   - Set Setup Status URL to: `https://your-url.com/setup-status`
3. After conversations, visit `/dashboard` to see your social intelligence insights

## Important Memory Detection

The app automatically highlights important social interactions based on:
- Multiple emotions in a single conversation
- Presence of intense emotion words ("very", "deeply", "meaningful", etc.)

## License

(Add license information here) 
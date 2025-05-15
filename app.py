import os
import json
import datetime
import traceback
import requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Make sure OPENAI_API_KEY is set in your .env file.")

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Path to people.json file
people_json_path = data_dir / "people.json"

# Initialize people.json if it doesn't exist
if not people_json_path.exists():
    with open(people_json_path, "w") as f:
        json.dump([], f)


def extract_insights_with_gpt(memory_text):
    """Extract relationship insights using GPT-4o."""
    prompt = f"""
    You are a relationship insight extractor. Given this memory text, extract the following:
    - People mentioned (with names)
    - Locations (e.g., cities, schools, places)
    - Emotions (positive or negative feelings expressed)
    - Social intent (e.g., reconnect, argument, bonding)

    Text:
    "{memory_text}"

    Return as JSON:
    {{
      "people": [...],
      "locations": [...],
      "emotions": [...],
      "social_intent": "..."
    }}
    """

    # Make a direct API request using requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.text}")
    
    response_data = response.json()
    return json.loads(response_data["choices"][0]["message"]["content"])


def generate_human_readable_summary(insights, memory_text):
    """Generate a concise, structured summary of the relationship insights."""
    prompt = f"""
    You are a relationship analyst. Based on the extracted insights and the original conversation, 
    create a concise, structured summary of the social interaction.
    
    Original conversation: 
    "{memory_text}"
    
    Extracted insights:
    People: {insights.get('people', [])}
    Locations: {insights.get('locations', [])}
    Emotions: {insights.get('emotions', [])}
    Social intent: {insights.get('social_intent', '')}
    
    Create a very concise summary in this EXACT format without any line breaks:
    
    📊 Social Intelligence: People: [key people] | Location: [location] | Emotions: [emotions] | Intent: [intent] | 🔥 Key insight: [brief insight]
    
    Keep it extremely brief but insightful. Do not use any newlines or special characters that might cause formatting issues when displayed in a mobile app.
    """

    # Make a direct API request using requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.text}")
    
    response_data = response.json()
    summary = response_data["choices"][0]["message"]["content"]
    
    # Print to terminal log for demo purposes
    print("\n" + "=" * 50)
    print("📊 NEW SOCIAL INTELLIGENCE SUMMARY:")
    print(summary)
    print("=" * 50 + "\n")
    
    return summary


def save_insight(insight, summary):
    """Save insight and summary to people.json."""
    # Add timestamp to insight
    entry = {
        "structured_data": insight,
        "human_summary": summary,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Load existing data
    with open(people_json_path, "r") as f:
        data = json.load(f)
    
    # Append new insight
    data.append(entry)
    
    # Save updated data
    with open(people_json_path, "w") as f:
        json.dump(data, f, indent=2)


def get_emotion_emoji(emotions):
    """Get an appropriate emoji based on emotions."""
    emotion_map = {
        "happy": "😄", "excited": "😄", "joy": "😄", "great": "😄", "positive": "😄",
        "awkward": "😬", "uncomfortable": "😬", "tense": "😬",
        "sad": "😢", "upset": "😢", "disappointed": "😢", "negative": "😢",
        "angry": "😠", "frustrated": "😠", "annoyed": "😠",
        "surprised": "😲", "shocked": "😲",
        "inspired": "✨", "motivated": "✨",
        "curious": "🤔", "confused": "🤔",
        "love": "❤️", "affection": "❤️",
        "miss": "💭", "nostalgia": "💭",
        "neutral": "😐"
    }
    
    if not emotions:
        return "😐"
    
    for emotion in emotions:
        emotion = emotion.lower()
        for key in emotion_map:
            if key in emotion:
                return emotion_map[key]
    
    return "😐"  # Default emoji


def is_important_memory(insight):
    """Determine if a memory is important based on criteria."""
    # Check if there are 2+ emotions
    emotions = insight.get("structured_data", {}).get("emotions", [])
    if len(emotions) >= 2:
        return True
    
    # Check for intense emotion words
    intense_words = ["very", "extremely", "deeply", "profound", "intense", "significant", "meaningful"]
    summary = insight.get("human_summary", "").lower()
    for word in intense_words:
        if word in summary:
            return True
    
    return False


@app.route("/", methods=["GET"])
def index():
    """Root endpoint with basic information."""
    return jsonify({
        "description": "An OMI Memory Trigger integration that extracts social intelligence data from conversation memories.",
        "endpoints": {
            "memory-trigger": "POST endpoint for receiving OMI memory data",
            "setup-status": "GET endpoint for checking setup status",
            "dashboard": "GET endpoint for visualizing social intelligence insights"
        },
        "instructions": "Visit /dashboard to see your social intelligence insights"
    })


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Dashboard page to visualize social intelligence insights."""
    # Load data from people.json
    with open(people_json_path, "r") as f:
        data = json.load(f)
    
    # Sort by timestamp (newest first)
    data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Process data for display
    insights = []
    for entry in data:
        if "structured_data" in entry:
            # For newer format entries
            structured_data = entry["structured_data"]
            summary = entry.get("human_summary", "No summary available")
            timestamp = entry.get("timestamp", "")
            
            # Get people and intent
            people = ", ".join(structured_data.get("people", []))
            intent = structured_data.get("social_intent", "unknown")
            emotions = structured_data.get("emotions", [])
            
            # Get emoji based on emotions
            emoji = get_emotion_emoji(emotions)
            
            # Check if this is an important memory
            is_important = is_important_memory(entry)
            
            insights.append({
                "timestamp": timestamp,
                "formatted_time": datetime.datetime.fromisoformat(timestamp).strftime("%b %d, %Y %I:%M %p") if timestamp else "Unknown time",
                "summary": summary,
                "people": people if people else "No people mentioned",
                "intent": intent,
                "emoji": emoji,
                "is_important": is_important
            })
        elif isinstance(entry, dict) and "people" in entry:
            # For older format entries
            people = ", ".join(entry.get("people", []))
            intent = entry.get("social_intent", "unknown")
            timestamp = entry.get("timestamp", "")
            emotions = entry.get("emotions", [])
            
            # Get emoji based on emotions
            emoji = get_emotion_emoji(emotions)
            
            # Create a simple summary
            locations = ", ".join(entry.get("locations", []))
            emotions_str = ", ".join(emotions)
            summary = f"People: {people} | Location: {locations} | Emotions: {emotions_str} | Intent: {intent}"
            
            # Check if this is an important memory
            is_important = len(emotions) >= 2
            
            insights.append({
                "timestamp": timestamp,
                "formatted_time": datetime.datetime.fromisoformat(timestamp).strftime("%b %d, %Y %I:%M %p") if timestamp else "Unknown time",
                "summary": summary,
                "people": people if people else "No people mentioned",
                "intent": intent,
                "emoji": emoji,
                "is_important": is_important
            })
    
    # HTML template for the dashboard
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Social Intelligence Dashboard</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f7;
            }
            h1 {
                color: #1d1d1f;
                font-size: 28px;
                margin-bottom: 20px;
                text-align: center;
            }
            .insights-container {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 30px;
            }
            ul {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            li {
                border-bottom: 1px solid #e1e1e1;
                padding: 15px 0;
                position: relative;
            }
            li:last-child {
                border-bottom: none;
            }
            .timestamp {
                color: #666;
                font-size: 14px;
                margin-bottom: 5px;
            }
            .summary {
                margin-bottom: 8px;
                font-size: 16px;
            }
            .meta {
                display: flex;
                align-items: center;
                font-size: 14px;
                color: #666;
            }
            .emoji {
                font-size: 24px;
                margin-right: 10px;
            }
            .important {
                background-color: #fff9e6;
                border-left: 4px solid #ffcc00;
                padding-left: 15px;
            }
            .tag {
                display: inline-block;
                background-color: #e1e1e1;
                border-radius: 12px;
                padding: 3px 8px;
                margin-right: 8px;
                font-size: 12px;
            }
            .intent-tag {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            .fire-icon {
                position: absolute;
                top: 15px;
                right: 15px;
                font-size: 20px;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin-bottom: 20px;
                text-align: center;
            }
            .stat-box {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                width: 30%;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .stat-number {
                font-size: 24px;
                font-weight: bold;
                color: #1d1d1f;
                margin-bottom: 5px;
            }
            .stat-label {
                font-size: 14px;
                color: #666;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .logo {
                font-size: 24px;
                font-weight: bold;
            }
            .last-updated {
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📊 Social Intelligence</div>
            <div class="last-updated">Last updated: {{ last_updated }}</div>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ total_insights }}</div>
                <div class="stat-label">Total Memories</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ important_count }}</div>
                <div class="stat-label">Important</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ unique_people }}</div>
                <div class="stat-label">People</div>
            </div>
        </div>
        
        <div class="insights-container">
            <h1>Recent Social Insights</h1>
            <ul>
                {% for insight in insights %}
                <li class="{{ 'important' if insight.is_important else '' }}">
                    {% if insight.is_important %}
                    <div class="fire-icon">🔥</div>
                    {% endif %}
                    <div class="timestamp">{{ insight.formatted_time }}</div>
                    <div class="summary">
                        <span class="emoji">{{ insight.emoji }}</span>
                        {{ insight.summary }}
                    </div>
                    <div class="meta">
                        {% if insight.people %}
                        <span class="tag">👤 {{ insight.people }}</span>
                        {% endif %}
                        <span class="tag intent-tag">🎯 {{ insight.intent }}</span>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Calculate stats
    total_insights = len(insights)
    important_count = sum(1 for insight in insights if insight["is_important"])
    
    # Get unique people
    all_people = set()
    for insight in insights:
        people = insight["people"].split(", ")
        for person in people:
            if person != "No people mentioned":
                all_people.add(person)
    unique_people = len(all_people)
    
    # Get last updated time
    last_updated = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
    
    # Render the template
    return render_template_string(
        template, 
        insights=insights, 
        total_insights=total_insights,
        important_count=important_count,
        unique_people=unique_people,
        last_updated=last_updated
    )


@app.route("/memory-trigger", methods=["GET"])
def memory_trigger_info():
    """Information about the memory trigger endpoint."""
    return jsonify({
        "endpoint": "memory-trigger",
        "method": "POST",
        "description": "Endpoint for receiving OMI memory data. Please use POST method with memory data in JSON format.",
        "example": "POST /memory-trigger?uid=user123 with memory data as JSON payload"
    })

@app.route("/memory-trigger", methods=["POST"])
def memory_trigger():
    """Handle OMI memory trigger webhook."""
    try:
        # Get the uid parameter from the query string
        uid = request.args.get("uid", "unknown_user")
        
        memory = request.json
        
        # Extract memory text from either structured overview or transcript segments
        memory_text = ""
        if memory.get("structured") and memory["structured"].get("overview"):
            memory_text = memory["structured"]["overview"]
        elif memory.get("transcript_segments"):
            memory_text = " ".join([segment["text"] for segment in memory["transcript_segments"]])
        
        if not memory_text:
            return jsonify({"status": "error", "message": "No memory text found"}), 400
        
        # Extract insights
        extracted = extract_insights_with_gpt(memory_text)
        
        # Add uid to the extracted data
        extracted["uid"] = uid
        
        # Generate human-readable summary
        human_summary = generate_human_readable_summary(extracted, memory_text)
        
        # Format the summary as a clean string without escaped newlines
        # This will make it display properly in the OMI app
        formatted_summary = human_summary.replace('\n', ' ').strip()
        
        # Get dashboard URL (use ngrok URL if available, otherwise use localhost)
        dashboard_url = f"{request.host_url}dashboard"
        
        # Add clickable dashboard link
        formatted_summary_with_link = f"{formatted_summary}\n\n👉 [View Social Intelligence Dashboard]({dashboard_url})"
        
        # Save insight and summary
        save_insight(extracted, human_summary)
        
        # Return a cleaner response format
        return jsonify({
            "status": "ok",
            "extracted": extracted,
            "summary": formatted_summary_with_link
        })
    
    except Exception as e:
        print(f"Error in memory_trigger: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/setup-status", methods=["GET"])
def setup_status():
    """Return setup status."""
    return jsonify({"is_setup_completed": True})


@app.route("/omi-dashboard", methods=["POST"])
def omi_dashboard():
    """Dashboard endpoint compatible with OMI's webhook system."""
    try:
        # Load data from people.json
        with open(people_json_path, "r") as f:
            data = json.load(f)
        
        # Sort by timestamp (newest first)
        data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Take only the 5 most recent insights
        recent_data = data[:5]
        
        # Format insights for OMI display
        insights_text = ""
        for i, entry in enumerate(recent_data):
            if "structured_data" in entry:
                # For newer format entries
                structured_data = entry["structured_data"]
                emotions = structured_data.get("emotions", [])
                emoji = get_emotion_emoji(emotions)
                
                # Get people and intent
                people = ", ".join(structured_data.get("people", []))
                intent = structured_data.get("social_intent", "unknown")
                
                # Format timestamp
                timestamp = entry.get("timestamp", "")
                formatted_time = datetime.datetime.fromisoformat(timestamp).strftime("%b %d") if timestamp else "Unknown"
                
                # Check if this is an important memory
                is_important = is_important_memory(entry)
                important_marker = "🔥 " if is_important else ""
                
                # Get summary or create one
                if "human_summary" in entry:
                    summary = entry["human_summary"]
                else:
                    # Create a simple summary for older entries
                    locations = ", ".join(structured_data.get("locations", []))
                    emotions_str = ", ".join(emotions)
                    summary = f"People: {people} | Location: {locations} | Emotions: {emotions_str} | Intent: {intent}"
                
                # Format the insight
                insights_text += f"{important_marker}{emoji} {formatted_time}: {summary}\n\n"
            
        # Create a response that OMI can display
        response_text = f"""📊 Social Intelligence Dashboard

Recent Insights:

{insights_text}

View full dashboard: {request.host_url}dashboard
"""
        
        return jsonify({
            "text": response_text
        })
    
    except Exception as e:
        print(f"Error in omi_dashboard: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"text": f"Error loading dashboard: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001) 
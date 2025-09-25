#!/usr/bin/env python3
"""
Meeting Minutes Generator
Creates structured meeting minutes from video transcriptions.

Requirements:
    pip install openai python-dateutil jinja2

Usage:
    python meeting_minutes_generator.py transcription.txt --output meeting_minutes.html
    python meeting_minutes_generator.py transcription.txt --format pdf --api-key your_openai_key
"""

import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class MeetingMinutesGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None

    def parse_transcription(self, transcription_text):
        """Parse transcription text and extract speaker information."""
        lines = transcription_text.strip().split('\n')
        parsed_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match speaker patterns like "Speaker 1:", "John:", "[00:15:30] Speaker 1:"
            speaker_match = re.match(r'^(\[?(\d{2}:\d{2}:\d{2})\]?\s*)?([^:]+):\s*(.*)$', line)
            if speaker_match:
                timestamp = speaker_match.group(2)
                speaker = speaker_match.group(3).strip()
                content = speaker_match.group(4).strip()
                
                parsed_content.append({
                    'timestamp': timestamp,
                    'speaker': speaker,
                    'content': content
                })
            else:
                # If no speaker pattern, treat as continuation of previous content
                if parsed_content:
                    parsed_content[-1]['content'] += ' ' + line
                else:
                    # First line without speaker - create a default speaker
                    parsed_content.append({
                        'timestamp': None,
                        'speaker': 'Unknown',
                        'content': line
                    })
        
        return parsed_content

    def extract_key_points(self, parsed_content):
        """Extract key discussion points from the transcription."""
        if not self.client:
            return self._extract_key_points_simple(parsed_content)
        
        try:
            # Combine all content for AI analysis
            full_text = '\n'.join([f"{item['speaker']}: {item['content']}" for item in parsed_content])
            
            prompt = f"""
            Analyze this meeting transcription and extract the key discussion points, decisions, and important topics.
            Return a JSON list of key points, each with a 'topic' and 'summary' field.
            
            Transcription:
            {full_text[:4000]}  # Limit to avoid token limits
            
            Return only valid JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return self._extract_key_points_simple(parsed_content)
                
        except Exception as e:
            print(f"AI analysis failed: {e}. Using simple extraction.")
            return self._extract_key_points_simple(parsed_content)

    def _extract_key_points_simple(self, parsed_content):
        """Simple keyword-based key point extraction."""
        key_points = []
        content_text = ' '.join([item['content'] for item in parsed_content])
        
        # Look for decision indicators
        decision_keywords = ['decided', 'agreed', 'concluded', 'resolved', 'approved', 'rejected']
        for keyword in decision_keywords:
            if keyword in content_text.lower():
                # Find sentences containing the keyword
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        key_points.append({
                            'topic': f'Decision ({keyword.title()})',
                            'summary': sentence.strip()
                        })
                        break
        
        # Look for action items
        action_keywords = ['action', 'todo', 'task', 'follow up', 'next steps', 'will do']
        for keyword in action_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        key_points.append({
                            'topic': 'Action Item',
                            'summary': sentence.strip()
                        })
                        break
        
        return key_points[:5]  # Limit to 5 key points

    def extract_action_items(self, parsed_content):
        """Extract action items and next steps."""
        if not self.client:
            return self._extract_action_items_simple(parsed_content)
        
        try:
            full_text = '\n'.join([f"{item['speaker']}: {item['content']}" for item in parsed_content])
            
            prompt = f"""
            Extract action items and next steps from this meeting transcription.
            Return a JSON list of action items, each with 'action', 'assignee', and 'due_date' fields.
            If assignee or due_date cannot be determined, use null.
            
            Transcription:
            {full_text[:4000]}
            
            Return only valid JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return self._extract_action_items_simple(parsed_content)
                
        except Exception as e:
            print(f"AI action extraction failed: {e}. Using simple extraction.")
            return self._extract_action_items_simple(parsed_content)

    def _extract_action_items_simple(self, parsed_content):
        """Simple action item extraction."""
        action_items = []
        for item in parsed_content:
            content = item['content'].lower()
            if any(keyword in content for keyword in ['will do', 'action item', 'todo', 'follow up', 'next step']):
                action_items.append({
                    'action': item['content'],
                    'assignee': item['speaker'],
                    'due_date': None
                })
        
        return action_items

    def generate_summary(self, parsed_content):
        """Generate meeting summary."""
        if not self.client:
            return self._generate_summary_simple(parsed_content)
        
        try:
            full_text = '\n'.join([f"{item['speaker']}: {item['content']}" for item in parsed_content])
            
            prompt = f"""
            Write a concise summary of this meeting (2-3 paragraphs).
            Focus on the main topics discussed, key decisions made, and outcomes.
            
            Transcription:
            {full_text[:4000]}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI summary generation failed: {e}. Using simple summary.")
            return self._generate_summary_simple(parsed_content)

    def _generate_summary_simple(self, parsed_content):
        """Simple summary generation."""
        speakers = list(set([item['speaker'] for item in parsed_content]))
        total_duration = len(parsed_content) * 0.5  # Rough estimate
        
        summary = f"""
        Meeting Summary:
        This meeting involved {len(speakers)} participants: {', '.join(speakers)}.
        The discussion covered various topics with approximately {len(parsed_content)} exchanges.
        Key areas of discussion included project updates, decisions, and action items.
        """
        
        return summary.strip()

    def generate_meeting_minutes(self, transcription_text, meeting_title="Meeting Minutes", meeting_date=None):
        """Generate complete meeting minutes."""
        if meeting_date is None:
            meeting_date = datetime.now()
        
        # Parse transcription
        parsed_content = self.parse_transcription(transcription_text)
        
        # Extract information
        key_points = self.extract_key_points(parsed_content)
        action_items = self.extract_action_items(parsed_content)
        summary = self.generate_summary(parsed_content)
        
        # Get unique speakers
        speakers = list(set([item['speaker'] for item in parsed_content]))
        
        return {
            'title': meeting_title,
            'date': meeting_date,
            'speakers': speakers,
            'summary': summary,
            'key_points': key_points,
            'action_items': action_items,
            'transcription': parsed_content
        }

    def save_html(self, meeting_data, output_path):
        """Save meeting minutes as HTML."""
        if not JINJA2_AVAILABLE:
            return self._save_html_simple(meeting_data, output_path)
        
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .section { margin-bottom: 25px; }
        .section h2 { color: #333; border-left: 4px solid #007acc; padding-left: 10px; }
        .speaker { font-weight: bold; color: #007acc; }
        .timestamp { color: #666; font-size: 0.9em; }
        .action-item { background: #f0f8ff; padding: 10px; margin: 5px 0; border-left: 3px solid #007acc; }
        .key-point { background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 3px solid #28a745; }
        .transcription { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p><strong>Date:</strong> {{ date.strftime('%B %d, %Y at %I:%M %p') }}</p>
        <p><strong>Participants:</strong> {{ speakers | join(', ') }}</p>
    </div>

    <div class="section">
        <h2>Meeting Summary</h2>
        <p>{{ summary }}</p>
    </div>

    {% if key_points %}
    <div class="section">
        <h2>Key Discussion Points</h2>
        {% for point in key_points %}
        <div class="key-point">
            <strong>{{ point.topic }}:</strong> {{ point.summary }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if action_items %}
    <div class="section">
        <h2>Action Items</h2>
        {% for item in action_items %}
        <div class="action-item">
            <strong>Action:</strong> {{ item.action }}<br>
            {% if item.assignee %}<strong>Assignee:</strong> {{ item.assignee }}<br>{% endif %}
            {% if item.due_date %}<strong>Due Date:</strong> {{ item.due_date }}{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section">
        <h2>Full Transcription</h2>
        <div class="transcription">
            {% for item in transcription %}
            <p>
                {% if item.timestamp %}<span class="timestamp">[{{ item.timestamp }}]</span> {% endif %}
                <span class="speaker">{{ item.speaker }}:</span> {{ item.content }}
            </p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        html_content = template.render(**meeting_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _save_html_simple(self, meeting_data, output_path):
        """Simple HTML generation without Jinja2."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting_data['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 25px; }}
        .section h2 {{ color: #333; border-left: 4px solid #007acc; padding-left: 10px; }}
        .speaker {{ font-weight: bold; color: #007acc; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .action-item {{ background: #f0f8ff; padding: 10px; margin: 5px 0; border-left: 3px solid #007acc; }}
        .key-point {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 3px solid #28a745; }}
        .transcription {{ max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{meeting_data['title']}</h1>
        <p><strong>Date:</strong> {meeting_data['date'].strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>Participants:</strong> {', '.join(meeting_data['speakers'])}</p>
    </div>

    <div class="section">
        <h2>Meeting Summary</h2>
        <p>{meeting_data['summary']}</p>
    </div>

    <div class="section">
        <h2>Key Discussion Points</h2>
        {''.join([f'<div class="key-point"><strong>{point["topic"]}:</strong> {point["summary"]}</div>' for point in meeting_data['key_points']])}
    </div>

    <div class="section">
        <h2>Action Items</h2>
        {''.join([f'<div class="action-item"><strong>Action:</strong> {item["action"]}<br><strong>Assignee:</strong> {item["assignee"]}</div>' for item in meeting_data['action_items']])}
    </div>

    <div class="section">
        <h2>Full Transcription</h2>
        <div class="transcription">
            {''.join([f'<p><span class="speaker">{item["speaker"]}:</span> {item["content"]}</p>' for item in meeting_data['transcription']])}
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def save_json(self, meeting_data, output_path):
        """Save meeting minutes as JSON."""
        # Convert datetime to string for JSON serialization
        json_data = meeting_data.copy()
        json_data['date'] = meeting_data['date'].isoformat()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Generate meeting minutes from video transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python meeting_minutes_generator.py transcription.txt
    python meeting_minutes_generator.py transcription.txt --output minutes.html --format html
    python meeting_minutes_generator.py transcription.txt --api-key sk-... --format json
    python meeting_minutes_generator.py transcription.txt --title "Weekly Team Meeting" --date "2024-01-15"
        """
    )
    
    parser.add_argument(
        'transcription_file',
        help='Path to the transcription text file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: meeting_minutes.html)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['html', 'json'],
        default='html',
        help='Output format (default: html)'
    )
    
    parser.add_argument(
        '--api-key',
        help='OpenAI API key for AI-powered analysis'
    )
    
    parser.add_argument(
        '--title',
        default='Meeting Minutes',
        help='Meeting title (default: Meeting Minutes)'
    )
    
    parser.add_argument(
        '--date',
        help='Meeting date (YYYY-MM-DD format, default: today)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.transcription_file):
        print(f"Error: Transcription file '{args.transcription_file}' does not exist.")
        sys.exit(1)
    
    # Read transcription
    try:
        with open(args.transcription_file, 'r', encoding='utf-8') as f:
            transcription_text = f.read()
    except Exception as e:
        print(f"Error reading transcription file: {e}")
        sys.exit(1)
    
    # Parse meeting date
    meeting_date = datetime.now()
    if args.date:
        try:
            meeting_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Generate output filename
    if not args.output:
        base_name = Path(args.transcription_file).stem
        args.output = f"{base_name}_meeting_minutes.{args.format}"
    
    # Check dependencies
    if args.api_key and not OPENAI_AVAILABLE:
        print("Warning: OpenAI package not installed. Install with: pip install openai")
        print("Continuing without AI features...")
    
    if args.format == 'html' and not JINJA2_AVAILABLE:
        print("Warning: Jinja2 package not installed. Install with: pip install jinja2")
        print("Using simple HTML generation...")
    
    # Generate meeting minutes
    print("Generating meeting minutes...")
    generator = MeetingMinutesGenerator(api_key=args.api_key)
    
    try:
        meeting_data = generator.generate_meeting_minutes(
            transcription_text, 
            meeting_title=args.title,
            meeting_date=meeting_date
        )
        
        # Save output
        if args.format == 'html':
            generator.save_html(meeting_data, args.output)
        elif args.format == 'json':
            generator.save_json(meeting_data, args.output)
        
        print(f"Meeting minutes saved to: {args.output}")
        print(f"Participants: {', '.join(meeting_data['speakers'])}")
        print(f"Key points extracted: {len(meeting_data['key_points'])}")
        print(f"Action items found: {len(meeting_data['action_items'])}")
        
    except Exception as e:
        print(f"Error generating meeting minutes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

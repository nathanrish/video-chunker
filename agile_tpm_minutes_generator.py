#!/usr/bin/env python3
"""
Agile TPM Meeting Minutes Generator
Creates professional Agile Technical Program Manager style meeting minutes from transcriptions.

Features:
- Agile framework structure (Epics, Stories, Tasks)
- Risk and dependency tracking
- Action items with owners and due dates
- Technical decision documentation
- Stakeholder communication tracking

Requirements:
    pip install openai python-dateutil jinja2

Usage:
    python agile_tpm_minutes_generator.py transcription.txt --output tpm_meeting_minutes.html
    python agile_tpm_minutes_generator.py transcription.txt --format docx --api-key your_openai_key
"""

import os
import sys
import argparse
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

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


class AgileTPMMinutesGenerator:
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
                
            # Try to match speaker patterns
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
                # If no speaker pattern, treat as continuation
                if parsed_content:
                    parsed_content[-1]['content'] += ' ' + line
                else:
                    parsed_content.append({
                        'timestamp': None,
                        'speaker': 'Unknown',
                        'content': line
                    })
        
        return parsed_content

    def extract_agile_artifacts(self, parsed_content):
        """Extract Agile artifacts like epics, stories, tasks, etc."""
        if not self.client:
            return self._extract_agile_artifacts_simple(parsed_content)
        
        try:
            full_text = '\n'.join([f"{item['speaker']}: {item['content']}" for item in parsed_content])
            
            prompt = f"""
            Analyze this meeting transcription and extract Agile TPM artifacts in JSON format:
            
            1. Epics (major initiatives/features)
            2. User Stories (business requirements)
            3. Technical Tasks (implementation work)
            4. Risks (potential issues)
            5. Dependencies (blockers or prerequisites)
            6. Decisions (technical or business decisions made)
            7. Action Items (specific tasks with owners)
            
            Return a JSON object with these keys:
            {{
                "epics": [{{"title": "Epic name", "description": "Epic description", "priority": "High/Medium/Low"}}],
                "user_stories": [{{"title": "Story title", "description": "Story description", "acceptance_criteria": "Criteria"}}],
                "technical_tasks": [{{"title": "Task title", "description": "Task description", "effort": "Story points or time estimate"}}],
                "risks": [{{"title": "Risk title", "description": "Risk description", "impact": "High/Medium/Low", "probability": "High/Medium/Low"}}],
                "dependencies": [{{"title": "Dependency title", "description": "Dependency description", "blocker": "What it blocks"}}],
                "decisions": [{{"title": "Decision title", "description": "Decision description", "rationale": "Why this decision"}}],
                "action_items": [{{"action": "Action description", "owner": "Person responsible", "due_date": "Date or sprint", "priority": "High/Medium/Low"}}]
            }}
            
            Transcription:
            {full_text[:4000]}
            
            Return only valid JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return self._extract_agile_artifacts_simple(parsed_content)
                
        except Exception as e:
            print(f"AI analysis failed: {e}. Using simple extraction.")
            return self._extract_agile_artifacts_simple(parsed_content)

    def _extract_agile_artifacts_simple(self, parsed_content):
        """Simple keyword-based Agile artifact extraction."""
        artifacts = {
            "epics": [],
            "user_stories": [],
            "technical_tasks": [],
            "risks": [],
            "dependencies": [],
            "decisions": [],
            "action_items": []
        }
        
        content_text = ' '.join([item['content'] for item in parsed_content])
        
        # Extract epics (major features/initiatives)
        epic_keywords = ['epic', 'initiative', 'feature', 'release', 'milestone']
        for keyword in epic_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        artifacts["epics"].append({
                            "title": f"Epic: {keyword.title()}",
                            "description": sentence.strip(),
                            "priority": "Medium"
                        })
                        break
        
        # Extract risks
        risk_keywords = ['risk', 'concern', 'issue', 'problem', 'challenge', 'blocker']
        for keyword in risk_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        artifacts["risks"].append({
                            "title": f"Risk: {keyword.title()}",
                            "description": sentence.strip(),
                            "impact": "Medium",
                            "probability": "Medium"
                        })
                        break
        
        # Extract action items
        action_keywords = ['action', 'todo', 'task', 'follow up', 'next step', 'will do', 'need to']
        for keyword in action_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        artifacts["action_items"].append({
                            "action": sentence.strip(),
                            "owner": "TBD",
                            "due_date": "TBD",
                            "priority": "Medium"
                        })
                        break
        
        # Extract decisions
        decision_keywords = ['decided', 'decision', 'agree', 'approved', 'concluded', 'resolved']
        for keyword in decision_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        artifacts["decisions"].append({
                            "title": f"Decision: {keyword.title()}",
                            "description": sentence.strip(),
                            "rationale": "Discussed in meeting"
                        })
                        break
        
        return artifacts

    def extract_sprint_info(self, parsed_content):
        """Extract sprint and timeline information."""
        content_text = ' '.join([item['content'] for item in parsed_content])
        
        # Look for dates and deadlines
        date_patterns = [
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December))',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?)',
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content_text, re.IGNORECASE)
            dates.extend(matches)
        
        # Look for sprint references
        sprint_keywords = ['sprint', 'iteration', 'cycle', 'milestone', 'release']
        sprints = []
        for keyword in sprint_keywords:
            if keyword in content_text.lower():
                sentences = re.split(r'[.!?]+', content_text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        sprints.append(sentence.strip())
                        break
        
        return {
            "dates": list(set(dates)),
            "sprints": list(set(sprints))
        }

    def generate_tpm_summary(self, parsed_content, artifacts, sprint_info):
        """Generate TPM-style executive summary."""
        if not self.client:
            return self._generate_tpm_summary_simple(parsed_content, artifacts, sprint_info)
        
        try:
            full_text = '\n'.join([f"{item['speaker']}: {item['content']}" for item in parsed_content])
            
            prompt = f"""
            Write an executive summary for a Technical Program Manager meeting minutes document.
            Focus on:
            1. Key program status and progress
            2. Critical milestones and deadlines
            3. Major risks and blockers
            4. Resource and timeline implications
            5. Next steps and recommendations
            
            Meeting content:
            {full_text[:3000]}
            
            Extracted artifacts: {json.dumps(artifacts, indent=2)}
            Sprint info: {json.dumps(sprint_info, indent=2)}
            
            Write 2-3 paragraphs in a professional TPM style.
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
            return self._generate_tpm_summary_simple(parsed_content, artifacts, sprint_info)

    def _generate_tpm_summary_simple(self, parsed_content, artifacts, sprint_info):
        """Simple TPM summary generation."""
        total_actions = len(artifacts.get("action_items", []))
        total_risks = len(artifacts.get("risks", []))
        total_decisions = len(artifacts.get("decisions", []))
        
        summary = f"""
        Program Status Update: This meeting covered key program activities with {total_actions} action items identified, {total_risks} risks discussed, and {total_decisions} decisions made. 
        
        Critical milestones and deadlines were reviewed, with focus on upcoming deliverables and stakeholder commitments. Key risks and dependencies were identified that may impact program timeline and resource allocation.
        
        Next steps include addressing identified action items, monitoring risk mitigation efforts, and ensuring alignment across all program stakeholders for successful delivery.
        """
        
        return summary.strip()

    def generate_agile_tpm_minutes(self, transcription_text, meeting_title="TPM Meeting Minutes", meeting_date=None):
        """Generate complete Agile TPM meeting minutes."""
        if meeting_date is None:
            meeting_date = datetime.now()
        
        # Parse transcription
        parsed_content = self.parse_transcription(transcription_text)
        
        # Extract Agile artifacts
        artifacts = self.extract_agile_artifacts(parsed_content)
        
        # Extract sprint/timeline info
        sprint_info = self.extract_sprint_info(parsed_content)
        
        # Generate TPM summary
        tpm_summary = self.generate_tpm_summary(parsed_content, artifacts, sprint_info)
        
        # Get unique speakers
        speakers = list(set([item['speaker'] for item in parsed_content]))
        
        return {
            'title': meeting_title,
            'date': meeting_date,
            'speakers': speakers,
            'tpm_summary': tpm_summary,
            'artifacts': artifacts,
            'sprint_info': sprint_info,
            'transcription': parsed_content
        }

    def save_agile_tpm_html(self, meeting_data, output_path):
        """Save Agile TPM meeting minutes as HTML."""
        if not JINJA2_AVAILABLE:
            return self._save_agile_tpm_html_simple(meeting_data, output_path)
        
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section { background: white; margin-bottom: 20px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; border-left: 4px solid #3498db; padding-left: 15px; margin-top: 0; }
        .section h3 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }
        .speaker { font-weight: bold; color: #3498db; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .epic { background: #e8f5e8; border-left: 4px solid #27ae60; padding: 10px; margin: 5px 0; }
        .story { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px; margin: 5px 0; }
        .task { background: #fff3e0; border-left: 4px solid #ff9800; padding: 10px; margin: 5px 0; }
        .risk { background: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 5px 0; }
        .dependency { background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 10px; margin: 5px 0; }
        .decision { background: #e0f2f1; border-left: 4px solid #009688; padding: 10px; margin: 5px 0; }
        .action-item { background: #fff8e1; border-left: 4px solid #ffc107; padding: 10px; margin: 5px 0; }
        .priority-high { border-left-color: #e74c3c !important; }
        .priority-medium { border-left-color: #f39c12 !important; }
        .priority-low { border-left-color: #27ae60 !important; }
        .transcription { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background: #fafafa; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .metric { text-align: center; padding: 10px; background: #ecf0f1; border-radius: 5px; }
        .metric-number { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .metric-label { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p><strong>Date:</strong> {{ date.strftime('%B %d, %Y at %I:%M %p') }}</p>
        <p><strong>Participants:</strong> {{ speakers | join(', ') }}</p>
        <p><strong>Meeting Type:</strong> Agile TPM Program Review</p>
    </div>

    <div class="section">
        <h2>📊 Program Metrics</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-number">{{ artifacts.epics | length }}</div>
                <div class="metric-label">Epics</div>
            </div>
            <div class="metric">
                <div class="metric-number">{{ artifacts.user_stories | length }}</div>
                <div class="metric-label">User Stories</div>
            </div>
            <div class="metric">
                <div class="metric-number">{{ artifacts.technical_tasks | length }}</div>
                <div class="metric-label">Technical Tasks</div>
            </div>
            <div class="metric">
                <div class="metric-number">{{ artifacts.risks | length }}</div>
                <div class="metric-label">Risks</div>
            </div>
            <div class="metric">
                <div class="metric-number">{{ artifacts.action_items | length }}</div>
                <div class="metric-label">Action Items</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📋 Executive Summary</h2>
        <p>{{ tpm_summary }}</p>
    </div>

    {% if artifacts.epics %}
    <div class="section">
        <h2>🎯 Epics & Major Initiatives</h2>
        {% for epic in artifacts.epics %}
        <div class="epic priority-{{ epic.priority.lower() }}">
            <strong>{{ epic.title }}</strong><br>
            {{ epic.description }}<br>
            <small>Priority: {{ epic.priority }}</small>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.user_stories %}
    <div class="section">
        <h2>📖 User Stories</h2>
        {% for story in artifacts.user_stories %}
        <div class="story">
            <strong>{{ story.title }}</strong><br>
            {{ story.description }}<br>
            {% if story.acceptance_criteria %}<small>Acceptance Criteria: {{ story.acceptance_criteria }}</small>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.technical_tasks %}
    <div class="section">
        <h2>⚙️ Technical Tasks</h2>
        {% for task in artifacts.technical_tasks %}
        <div class="task">
            <strong>{{ task.title }}</strong><br>
            {{ task.description }}<br>
            {% if task.effort %}<small>Effort: {{ task.effort }}</small>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.risks %}
    <div class="section">
        <h2>⚠️ Risks & Issues</h2>
        {% for risk in artifacts.risks %}
        <div class="risk priority-{{ risk.impact.lower() }}">
            <strong>{{ risk.title }}</strong><br>
            {{ risk.description }}<br>
            <small>Impact: {{ risk.impact }} | Probability: {{ risk.probability }}</small>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.dependencies %}
    <div class="section">
        <h2>🔗 Dependencies & Blockers</h2>
        {% for dep in artifacts.dependencies %}
        <div class="dependency">
            <strong>{{ dep.title }}</strong><br>
            {{ dep.description }}<br>
            {% if dep.blocker %}<small>Blocks: {{ dep.blocker }}</small>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.decisions %}
    <div class="section">
        <h2>✅ Decisions Made</h2>
        {% for decision in artifacts.decisions %}
        <div class="decision">
            <strong>{{ decision.title }}</strong><br>
            {{ decision.description }}<br>
            {% if decision.rationale %}<small>Rationale: {{ decision.rationale }}</small>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if artifacts.action_items %}
    <div class="section">
        <h2>📝 Action Items</h2>
        {% for item in artifacts.action_items %}
        <div class="action-item priority-{{ item.priority.lower() }}">
            <strong>Action:</strong> {{ item.action }}<br>
            <strong>Owner:</strong> {{ item.owner }}<br>
            <strong>Due Date:</strong> {{ item.due_date }}<br>
            <small>Priority: {{ item.priority }}</small>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if sprint_info.dates or sprint_info.sprints %}
    <div class="section">
        <h2>📅 Timeline & Milestones</h2>
        {% if sprint_info.dates %}
        <h3>Key Dates</h3>
        <ul>
            {% for date in sprint_info.dates %}
            <li>{{ date }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% if sprint_info.sprints %}
        <h3>Sprint References</h3>
        <ul>
            {% for sprint in sprint_info.sprints %}
            <li>{{ sprint }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    {% endif %}

    <div class="section">
        <h2>💬 Full Transcription</h2>
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

    def _save_agile_tpm_html_simple(self, meeting_data, output_path):
        """Simple HTML generation without Jinja2."""
        artifacts = meeting_data['artifacts']
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting_data['title']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .section {{ background: white; margin-bottom: 20px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #2c3e50; border-left: 4px solid #3498db; padding-left: 15px; margin-top: 0; }}
        .epic {{ background: #e8f5e8; border-left: 4px solid #27ae60; padding: 10px; margin: 5px 0; }}
        .risk {{ background: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 5px 0; }}
        .decision {{ background: #e0f2f1; border-left: 4px solid #009688; padding: 10px; margin: 5px 0; }}
        .action-item {{ background: #fff8e1; border-left: 4px solid #ffc107; padding: 10px; margin: 5px 0; }}
        .transcription {{ max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background: #fafafa; }}
        .speaker {{ font-weight: bold; color: #3498db; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{meeting_data['title']}</h1>
        <p><strong>Date:</strong> {meeting_data['date'].strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>Participants:</strong> {', '.join(meeting_data['speakers'])}</p>
        <p><strong>Meeting Type:</strong> Agile TPM Program Review</p>
    </div>

    <div class="section">
        <h2>📋 Executive Summary</h2>
        <p>{meeting_data['tpm_summary']}</p>
    </div>

    <div class="section">
        <h2>🎯 Epics & Major Initiatives</h2>
        {''.join([f'<div class="epic"><strong>{epic["title"]}</strong><br>{epic["description"]}<br><small>Priority: {epic["priority"]}</small></div>' for epic in artifacts.get('epics', [])])}
    </div>

    <div class="section">
        <h2>⚠️ Risks & Issues</h2>
        {''.join([f'<div class="risk"><strong>{risk["title"]}</strong><br>{risk["description"]}<br><small>Impact: {risk["impact"]} | Probability: {risk["probability"]}</small></div>' for risk in artifacts.get('risks', [])])}
    </div>

    <div class="section">
        <h2>✅ Decisions Made</h2>
        {''.join([f'<div class="decision"><strong>{decision["title"]}</strong><br>{decision["description"]}<br><small>Rationale: {decision["rationale"]}</small></div>' for decision in artifacts.get('decisions', [])])}
    </div>

    <div class="section">
        <h2>📝 Action Items</h2>
        {''.join([f'<div class="action-item"><strong>Action:</strong> {item["action"]}<br><strong>Owner:</strong> {item["owner"]}<br><strong>Due Date:</strong> {item["due_date"]}<br><small>Priority: {item["priority"]}</small></div>' for item in artifacts.get('action_items', [])])}
    </div>

    <div class="section">
        <h2>💬 Full Transcription</h2>
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
        """Save Agile TPM meeting minutes as JSON."""
        # Convert datetime to string for JSON serialization
        json_data = meeting_data.copy()
        json_data['date'] = meeting_data['date'].isoformat()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Agile TPM style meeting minutes from transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python agile_tpm_minutes_generator.py transcription.txt
    python agile_tpm_minutes_generator.py transcription.txt --output tpm_minutes.html --format html
    python agile_tpm_minutes_generator.py transcription.txt --api-key sk-... --format json
    python agile_tpm_minutes_generator.py transcription.txt --title "Sprint Planning Meeting" --date "2024-01-15"
        """
    )
    
    parser.add_argument(
        'transcription_file',
        help='Path to the transcription text file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: agile_tpm_meeting_minutes.html)'
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
        default='Agile TPM Meeting Minutes',
        help='Meeting title (default: Agile TPM Meeting Minutes)'
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
    
    # Generate output filename if not provided
    if not args.output:
        base_name = Path(args.transcription_file).stem
        args.output = f"{base_name}_agile_tpm_minutes.{args.format}"
    
    # Check dependencies
    if args.api_key and not OPENAI_AVAILABLE:
        print("Warning: OpenAI package not installed. Install with: pip install openai")
        print("Continuing without AI features...")
    
    if args.format == 'html' and not JINJA2_AVAILABLE:
        print("Warning: Jinja2 package not installed. Install with: pip install jinja2")
        print("Using simple HTML generation...")
    
    # Generate Agile TPM meeting minutes
    print("Generating Agile TPM meeting minutes...")
    generator = AgileTPMMinutesGenerator(api_key=args.api_key)
    
    try:
        meeting_data = generator.generate_agile_tpm_minutes(
            transcription_text, 
            meeting_title=args.title,
            meeting_date=meeting_date
        )
        
        # Save output
        if args.format == 'html':
            generator.save_agile_tpm_html(meeting_data, args.output)
        elif args.format == 'json':
            generator.save_json(meeting_data, args.output)
        
        print(f"Agile TPM meeting minutes saved to: {args.output}")
        print(f"Participants: {', '.join(meeting_data['speakers'])}")
        print(f"Epics identified: {len(meeting_data['artifacts']['epics'])}")
        print(f"Risks identified: {len(meeting_data['artifacts']['risks'])}")
        print(f"Action items: {len(meeting_data['artifacts']['action_items'])}")
        print(f"Decisions made: {len(meeting_data['artifacts']['decisions'])}")
        
    except Exception as e:
        print(f"Error generating Agile TPM meeting minutes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

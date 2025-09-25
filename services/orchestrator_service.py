#!/usr/bin/env python3
"""
Workflow Orchestrator Service (inspired by Camunda/Conductor)
Coordinates the video -> transcription -> minutes -> file ops workflow.

Exposes REST endpoints to start workflows and query status.
Implements background execution with retries and step-by-step state tracking.
"""

import os
import sys
import json
import time
import uuid
import queue
import threading
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default service URLs (can be overridden via env)
TRANSCRIPTION_URL = os.getenv('TRANSCRIPTION_SERVICE_URL', 'http://localhost:5001')
MINUTES_URL = os.getenv('MEETING_MINUTES_SERVICE_URL', 'http://localhost:5002')
FILES_URL = os.getenv('FILE_MANAGEMENT_SERVICE_URL', 'http://localhost:5003')

# Retry policy defaults
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_SEC = 3


class WorkflowStatus:
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


@dataclass
class WorkflowStepResult:
    step: str
    success: bool
    started_at: str
    ended_at: str
    duration_sec: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class WorkflowInstance:
    id: str
    status: str
    input: Dict[str, Any]
    created_at: str
    updated_at: str
    steps: List[WorkflowStepResult] = field(default_factory=list)
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class OrchestratorEngine:
    def __init__(self,
                 transcription_url: str = TRANSCRIPTION_URL,
                 minutes_url: str = MINUTES_URL,
                 files_url: str = FILES_URL,
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 retry_backoff: int = DEFAULT_RETRY_BACKOFF_SEC):
        self.transcription_url = transcription_url
        self.minutes_url = minutes_url
        self.files_url = files_url
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        self._instances: Dict[str, WorkflowInstance] = {}
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()

        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    # Public API
    def start_workflow(self, payload: Dict[str, Any]) -> WorkflowInstance:
        wf_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        instance = WorkflowInstance(
            id=wf_id,
            status=WorkflowStatus.PENDING,
            input=payload,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._instances[wf_id] = instance
        self._queue.put(wf_id)
        logger.info(f"Queued workflow {wf_id}")
        return instance

    def get_instance(self, wf_id: str) -> Optional[WorkflowInstance]:
        with self._lock:
            return self._instances.get(wf_id)

    def list_instances(self, limit: int = 50, status: Optional[str] = None) -> List[WorkflowInstance]:
        with self._lock:
            items = list(self._instances.values())
        if status:
            items = [i for i in items if i.status == status]
        # Sort by created_at desc
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items[:limit]

    # Worker
    def _worker_loop(self):
        while True:
            try:
                wf_id = self._queue.get()
                instance = self.get_instance(wf_id)
                if not instance:
                    continue
                self._run_instance(instance)
            except Exception as e:
                logger.exception(f"Worker loop error: {e}")

    def _update_status(self, instance: WorkflowInstance, status: str):
        instance.status = status
        instance.updated_at = datetime.now().isoformat()

    def _record_step(self, instance: WorkflowInstance, step: str, fn, *, retries: int = None, **kwargs) -> Dict[str, Any]:
        started = time.time()
        started_at = datetime.now().isoformat()
        attempt = 0
        last_error = None
        max_retries = self.max_retries if retries is None else retries

        while attempt <= max_retries:
            try:
                result = fn(**kwargs)
                ended = time.time()
                step_result = WorkflowStepResult(
                    step=step,
                    success=True,
                    started_at=started_at,
                    ended_at=datetime.now().isoformat(),
                    duration_sec=ended - started,
                    details=result
                )
                instance.steps.append(step_result)
                self._update_status(instance, instance.status)  # update timestamp
                return result
            except Exception as e:
                last_error = str(e)
                attempt += 1
                if attempt > max_retries:
                    ended = time.time()
                    step_result = WorkflowStepResult(
                        step=step,
                        success=False,
                        started_at=started_at,
                        ended_at=datetime.now().isoformat(),
                        duration_sec=ended - started,
                        error=last_error
                    )
                    instance.steps.append(step_result)
                    self._update_status(instance, instance.status)
                    raise
                # backoff
                time.sleep(self.retry_backoff * attempt)

    # Actual step callouts
    def _call_transcription(self, video_path: str, language: Optional[str]) -> Dict[str, Any]:
        payload = {"video_path": video_path, "language": language, "word_timestamps": True}
        r = requests.post(f"{self.transcription_url}/transcribe", json=payload, timeout=600)
        if r.status_code != 200:
            raise Exception(f"transcribe HTTP {r.status_code}")
        data = r.json()
        if not data.get("success"):
            raise Exception(f"transcribe failed: {data.get('error')}")
        return data

    def _format_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(f"{self.transcription_url}/format-transcript", json={"transcript_data": transcript_data}, timeout=60)
        if r.status_code != 200:
            raise Exception(f"format HTTP {r.status_code}")
        data = r.json()
        if not data.get("success"):
            raise Exception(f"format failed: {data.get('error')}")
        return data

    def _generate_minutes(self, transcription_text: str, meeting_title: str, meeting_date: Optional[str]) -> Dict[str, Any]:
        payload = {"transcription_text": transcription_text, "meeting_title": meeting_title, "meeting_date": meeting_date}
        r = requests.post(f"{self.minutes_url}/generate-minutes", json=payload, timeout=180)
        if r.status_code != 200:
            raise Exception(f"minutes HTTP {r.status_code}")
        data = r.json()
        if not data.get("success"):
            raise Exception(f"minutes failed: {data.get('error')}")
        return data

    def _create_folder(self, meeting_title: str, meeting_date: Optional[str]) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/create-dated-folder", json={"meeting_title": meeting_title, "meeting_date": meeting_date}, timeout=30)
        if r.status_code != 200:
            raise Exception(f"folder HTTP {r.status_code}")
        data = r.json()
        if not data.get("success"):
            raise Exception(f"folder failed: {data.get('error')}")
        return data

    def _save_transcript(self, transcript_text: str, output_folder: str) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/save-transcript", json={"transcript_text": transcript_text, "output_folder": output_folder, "filename": "transcript.txt"}, timeout=60)
        if r.status_code != 200:
            raise Exception(f"save transcript HTTP {r.status_code}")
        return r.json()

    def _save_docx(self, meeting_data: Dict[str, Any], output_folder: str) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/save-meeting-minutes-docx", json={"meeting_data": meeting_data, "output_folder": output_folder, "filename": "meeting_minutes.docx"}, timeout=120)
        if r.status_code != 200:
            raise Exception(f"save docx HTTP {r.status_code}")
        return r.json()

    def _save_html(self, meeting_data: Dict[str, Any], output_folder: str) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/save-meeting-minutes-html", json={"meeting_data": meeting_data, "output_folder": output_folder, "filename": "meeting_minutes.html"}, timeout=60)
        if r.status_code != 200:
            raise Exception(f"save html HTTP {r.status_code}")
        return r.json()

    def _copy_video(self, video_path: str, output_folder: str) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/copy-video", json={"video_path": video_path, "output_folder": output_folder}, timeout=120)
        if r.status_code != 200:
            raise Exception(f"copy video HTTP {r.status_code}")
        return r.json()

    def _create_summary(self, output_folder: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(f"{self.files_url}/create-workflow-summary", json={"output_folder": output_folder, "workflow_data": workflow_data}, timeout=60)
        if r.status_code != 200:
            raise Exception(f"summary HTTP {r.status_code}")
        return r.json()

    def _run_instance(self, instance: WorkflowInstance):
        self._update_status(instance, WorkflowStatus.RUNNING)
        payload = instance.input

        video_path = payload.get('video_path')
        meeting_title = payload.get('meeting_title')
        meeting_date = payload.get('meeting_date')  # ISO string
        language = payload.get('language')
        copy_video = bool(payload.get('copy_video', True))

        try:
            # Step 1: transcribe
            transcribe = self._record_step(
                instance,
                'transcription',
                self._call_transcription,
                video_path=video_path,
                language=language
            )

            # Step 2: format
            fmt = self._record_step(
                instance,
                'format_transcript',
                self._format_transcript,
                transcript_data=transcribe['data']
            )
            formatted_text = fmt.get('formatted_text')

            # Step 3: minutes
            minutes = self._record_step(
                instance,
                'generate_meeting_minutes',
                self._generate_minutes,
                transcription_text=formatted_text,
                meeting_title=meeting_title,
                meeting_date=meeting_date
            )
            meeting_data = minutes.get('data')

            # Step 4: create folder
            folder = self._record_step(
                instance,
                'create_output_folder',
                self._create_folder,
                meeting_title=meeting_title,
                meeting_date=meeting_date
            )
            output_folder = folder.get('folder_path')

            # Step 5: save transcript
            tr_file = self._record_step(
                instance,
                'save_transcript',
                self._save_transcript,
                transcript_text=formatted_text,
                output_folder=output_folder
            )

            # Step 6: save docx
            docx_file = self._record_step(
                instance,
                'save_meeting_minutes_docx',
                self._save_docx,
                meeting_data=meeting_data,
                output_folder=output_folder
            )

            # Step 7: save html
            html_file = self._record_step(
                instance,
                'save_meeting_minutes_html',
                self._save_html,
                meeting_data=meeting_data,
                output_folder=output_folder
            )

            # Step 8: copy video (optional)
            video_copy = None
            if copy_video:
                video_copy = self._record_step(
                    instance,
                    'copy_video',
                    self._copy_video,
                    video_path=video_path,
                    output_folder=output_folder
                )

            # Step 9: summary
            workflow_data = {
                'video_path': video_path,
                'meeting_title': meeting_title,
                'meeting_date': meeting_date or datetime.now().isoformat(),
                'language': language,
                'steps': [asdict(s) for s in instance.steps]
            }
            summary = self._record_step(
                instance,
                'create_workflow_summary',
                self._create_summary,
                output_folder=output_folder,
                workflow_data=workflow_data
            )

            instance.output = {
                'output_folder': output_folder,
                'files': {
                    'transcript': tr_file.get('file_path'),
                    'meeting_minutes_docx': docx_file.get('file_path'),
                    'meeting_minutes_html': html_file.get('file_path'),
                    'original_video': (video_copy or {}).get('file_path') if copy_video else None,
                    'workflow_summary': summary.get('file_path')
                }
            }
            self._update_status(instance, WorkflowStatus.COMPLETED)
            logger.info(f"Workflow {instance.id} completed")
        except Exception as e:
            instance.error = str(e)
            self._update_status(instance, WorkflowStatus.FAILED)
            logger.error(f"Workflow {instance.id} failed: {e}")


# Flask API
if FLASK_AVAILABLE:
    app = Flask(__name__)
    engine = OrchestratorEngine()

    @app.route('/health', methods=['GET'])
    def health():
        # Optionally ping dependencies
        deps = {}
        for name, url, path in [
            ('transcription', TRANSCRIPTION_URL, '/health'),
            ('meeting_minutes', MINUTES_URL, '/health'),
            ('file_management', FILES_URL, '/health'),
        ]:
            try:
                r = requests.get(url + path, timeout=2)
                deps[name] = {'ok': r.status_code == 200}
            except Exception as e:
                deps[name] = {'ok': False, 'error': str(e)}
        return jsonify({'status': 'healthy', 'service': 'orchestrator', 'dependencies': deps})

    @app.route('/workflows', methods=['POST'])
    def start_workflow():
        data = request.get_json() or {}
        # Required params
        for k in ['video_path', 'meeting_title']:
            if k not in data:
                return jsonify({'success': False, 'error': f'{k} is required'}), 400
        instance = engine.start_workflow({
            'video_path': data['video_path'],
            'meeting_title': data['meeting_title'],
            'meeting_date': data.get('meeting_date'),  # ISO string
            'language': data.get('language'),
            'copy_video': bool(data.get('copy_video', True))
        })
        return jsonify({'success': True, 'data': {'id': instance.id, 'status': instance.status, 'created_at': instance.created_at}}), 202

    @app.route('/workflows/<wf_id>', methods=['GET'])
    def get_workflow(wf_id: str):
        instance = engine.get_instance(wf_id)
        if not instance:
            return jsonify({'success': False, 'error': 'not found'}), 404
        return jsonify({'success': True, 'data': asdict(instance)})

    @app.route('/workflows', methods=['GET'])
    def list_workflows():
        limit = int(request.args.get('limit', 50))
        status = request.args.get('status')
        items = [asdict(i) for i in engine.list_instances(limit=limit, status=status)]
        return jsonify({'success': True, 'data': items, 'count': len(items)})

    def run_service(host='localhost', port=5000, debug=False):
        logger.info(f"Starting Orchestrator Service on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
else:
    def run_service(host='localhost', port=5000, debug=False):
        logger.error("Flask not available. Cannot run orchestrator service.")
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Workflow Orchestrator Service')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    run_service(host=args.host, port=args.port, debug=args.debug)

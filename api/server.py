from flask import Flask, request, jsonify  # type: ignore
from flask_restx import Api, Resource, fields  # type: ignore
from celery import Celery, chain  # type: ignore
from sqlalchemy import create_engine, Column, Integer, String, Text  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
import subprocess
import uuid
import json
import os

app = Flask(__name__)
api = Api(app, version='1.0', title='LemonBooster API',
          description='API for running security tools and pipelines',
          doc='/swagger/')

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# SQLAlchemy configuration
engine = create_engine('sqlite:////opt/results/jobs.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)
    status = Column(String)
    tool = Column(String)
    args = Column(Text)
    result = Column(Text)


Base.metadata.create_all(engine)

# Pipeline definitions
PIPELINES = {
    "content_discovery": [
        {"tool": "subfinder", "args": ["-d"]},
        {"tool": "httpx", "args": []},
        {"tool": "gobuster", "args": ["dir", "-u"]},
        {"tool": "linkfinder", "args": ["-i"]},
        {"tool": "gowitness", "args": ["single"]}
    ]
    # Add more pipelines here
}

# API models
run_model = api.model('Run', {
    'tool': fields.String(required=True, description='Name of the tool to run'),
    'args': fields.List(fields.String, description='Arguments for the tool')
})

pipeline_model = api.model('Pipeline', {
    'pipeline': fields.String(required=True, description='Name of the pipeline to run'),
    'target': fields.String(required=True, description='Target for the pipeline')
})


@celery.task(bind=True, name='server.run_tool_task')
def run_tool_task(self, tool, args, input_data=None):
    try:
        command = [tool] + args
        if input_data:
            # Pass input_data as input to the command
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=input_data)
            returncode = process.returncode
        else:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode

        output = {
            'stdout': stdout,
            'stderr': stderr,
            'returncode': returncode
        }
    except Exception as e:
        output = {'error': str(e)}

    # Update progress
    self.update_state(state='PROGRESS', meta={'current': self.request.chain.index(
        self.request.id) + 1, 'total': len(self.request.chain)})

    session = Session()
    job = session.query(Job).get(self.request.id)
    job.status = 'completed'
    job.result = json.dumps(output)
    session.commit()
    session.close()

    return output


@celery.task(bind=True, name='server.run_pipeline_task')
def run_pipeline_task(self, pipeline_name, target):
    pipeline = PIPELINES.get(pipeline_name)
    if not pipeline:
        return {'error': 'Pipeline not found'}

    # Create a chain of tasks
    tasks = []
    for step in pipeline:
        tool = step["tool"]
        args = step["args"] + [target]
        tasks.append(run_tool_task.s(tool, args))

    # Execute the chain of tasks
    chain_result = chain(*tasks).apply_async()

    # Store the chain ID for tracking
    session = Session()
    new_job = Job(id=chain_result.id, status="running",
                  tool=pipeline_name, args=target)
    session.add(new_job)
    session.commit()
    session.close()

    return {'chain_id': chain_result.id}


@api.route('/run')
class RunTool(Resource):
    @api.expect(run_model)
    @api.response(202, 'Tool execution started')
    def post(self):
        data = api.payload
        tool = data.get('tool')
        args = data.get('args', [])

        if not tool:
            api.abort(400, "No tool specified")

        task = run_tool_task.delay(tool, args)

        session = Session()
        new_job = Job(id=task.id, status="running",
                      tool=tool, args=json.dumps(args))
        session.add(new_job)
        session.commit()
        session.close()

        return {
            'message': f'Running {tool} in background',
            'job_id': task.id
        }, 202


@api.route('/run_pipeline')
class RunPipeline(Resource):
    @api.expect(pipeline_model)
    @api.response(202, 'Pipeline execution started')
    def post(self):
        data = api.payload
        pipeline_name = data.get('pipeline')
        target = data.get('target')

        if not pipeline_name or not target:
            api.abort(400, "Pipeline name and target are required")

        result = run_pipeline_task.delay(pipeline_name, target)

        return {
            'message': f'Running {pipeline_name} pipeline in background',
            'chain_id': result.get('chain_id')
        }, 202


@api.route('/job_status/<string:job_id>')
class JobStatus(Resource):
    @api.response(200, 'Job status')
    @api.response(404, 'Job not found')
    def get(self, job_id):
        session = Session()
        job = session.query(Job).get(job_id)
        session.close()

        if not job:
            api.abort(404, "Job not found")

        return {
            'status': job.status,
            'tool': job.tool,
            'args': json.loads(job.args)
        }


@api.route('/pipeline_status/<string:chain_id>')
class PipelineStatus(Resource):
    @api.response(200, 'Pipeline status')
    @api.response(404, 'Pipeline not found')
    def get(self, chain_id):
        result = celery.AsyncResult(chain_id)
        if result.state == 'PENDING':
            response = {
                'state': result.state,
                'status': 'Pipeline is pending execution'
            }
        elif result.state != 'FAILURE':
            response = {
                'state': result.state,
                'current': result.info.get('current', 0) if isinstance(result.info, dict) else 0,
                'total': result.info.get('total', 1) if isinstance(result.info, dict) else 1,
                'status': 'Pipeline is in progress' if result.state == 'PROGRESS' else 'Pipeline completed'
            }
        else:
            response = {
                'state': result.state,
                'status': 'Pipeline failed',
                'error': str(result.info)
            }
        return response


@api.route('/job_result/<string:job_id>')
class JobResult(Resource):
    @api.response(200, 'Job result')
    @api.response(404, 'Job not found')
    @api.response(400, 'Job not completed yet')
    def get(self, job_id):
        session = Session()
        job = session.query(Job).get(job_id)
        session.close()

        if not job:
            api.abort(404, "Job not found")

        if job.status != 'completed':
            api.abort(400, "Job not completed yet")

        return json.loads(job.result)


@api.route('/pipeline_result/<string:chain_id>')
class PipelineResult(Resource):
    @api.response(200, 'Pipeline result')
    @api.response(404, 'Pipeline not found')
    def get(self, chain_id):
        result = celery.AsyncResult(chain_id)
        if result.ready():
            return result.get()
        else:
            api.abort(400, "Pipeline not completed yet")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

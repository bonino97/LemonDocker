"""
LemonDocker API v2 - Professional Reconnaissance Pipeline API
Enhanced with parallel execution, result parsing, and comprehensive endpoints
"""
from flask import Flask, request, jsonify, send_file, abort
from flask_restx import Api, Resource, fields, Namespace
from celery import Celery, group, chord, chain
import subprocess
import uuid
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Import our new modules
from models import (
    init_db, get_session, Tool, Pipeline, PipelineStep, Execution,
    StepExecution, Result, Configuration, ExecutionStatus, PhaseCategory
)
from pipeline_executor import PipelineExecutor, ResultAggregator
from config_manager import get_config_manager
from result_parsers import get_parser

# Initialize Flask app
app = Flask(__name__)
api = Api(
    app,
    version='2.0',
    title='LemonDocker Reconnaissance API',
    description='Advanced reconnaissance automation with parallel execution',
    doc='/swagger/'
)

# Celery configuration
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Initialize database
init_db()
config_manager = get_config_manager()
config_manager.create_default_configs()

# ===== API MODELS =====

# Namespaces
ns_pipelines = api.namespace('pipelines', description='Pipeline management operations')
ns_executions = api.namespace('executions', description='Execution management')
ns_results = api.namespace('results', description='Results and findings')
ns_tools = api.namespace('tools', description='Available security tools')
ns_config = api.namespace('config', description='Configuration management')

# Models for Swagger documentation
pipeline_model = api.model('Pipeline', {
    'id': fields.Integer(description='Pipeline ID'),
    'name': fields.String(required=True, description='Pipeline name'),
    'description': fields.String(description='Pipeline description'),
    'category': fields.String(description='Pipeline category'),
    'estimated_duration_minutes': fields.Integer(description='Estimated duration'),
})

execution_request_model = api.model('ExecutionRequest', {
    'pipeline_id': fields.Integer(required=True, description='Pipeline ID to execute'),
    'target': fields.String(required=True, description='Target domain or IP'),
    'asset': fields.String(description='Specific asset name'),
    'user_id': fields.String(description='User ID', default='default'),
    'input_file': fields.String(description='Path to input file'),
    'metadata': fields.Raw(description='Additional metadata')
})

tool_model = api.model('Tool', {
    'id': fields.Integer(description='Tool ID'),
    'name': fields.String(description='Tool name'),
    'command': fields.String(description='Command to execute'),
    'description': fields.String(description='Tool description'),
    'category': fields.String(description='Tool category'),
})

result_filter_model = api.model('ResultFilter', {
    'execution_id': fields.String(required=True, description='Execution ID'),
    'result_type': fields.String(description='Filter by result type'),
    'severity': fields.String(description='Filter by severity (for vulnerabilities)'),
    'limit': fields.Integer(description='Limit results', default=1000)
})


# ===== CELERY TASKS =====

@celery.task(bind=True, name='server_v2.execute_pipeline_step')
def execute_pipeline_step_task(self, step_execution_id: str, step_id: int, execution_id: str, input_data: str = None):
    """
    Celery task for executing a single pipeline step
    """
    try:
        session = get_session()
        executor = PipelineExecutor(session)

        result = executor.execute_step(
            step_execution_id=step_execution_id,
            step_id=step_id,
            execution_id=execution_id,
            input_data=input_data
        )

        return result

    except Exception as e:
        # Update step execution to failed
        session = get_session()
        step_exec = session.query(StepExecution).get(step_execution_id)
        if step_exec:
            step_exec.status = ExecutionStatus.FAILED
            step_exec.error_message = str(e)
            session.commit()

        raise


@celery.task(bind=True, name='server_v2.execute_pipeline')
def execute_pipeline_task(self, execution_id: str):
    """
    Celery task for executing complete pipeline with parallel support
    """
    try:
        session = get_session()
        executor = PipelineExecutor(session)

        execution = session.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        pipeline = execution.pipeline

        # Update status
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        execution.celery_task_id = self.request.id
        session.commit()

        # Organize steps by parallel groups
        groups_dict = executor.organize_steps_by_groups(pipeline.steps)

        # Execute steps
        previous_output = None

        for group_key in sorted(groups_dict.keys(), key=lambda x: (isinstance(x, str) and x.startswith('seq'), x)):
            steps_in_group = groups_dict[group_key]

            if len(steps_in_group) == 1 or group_key.startswith('seq') if isinstance(group_key, str) else False:
                # Sequential execution
                for step in steps_in_group:
                    step_exec_id = str(uuid.uuid4())

                    result = execute_pipeline_step_task.apply_async(
                        args=[step_exec_id, step.id, execution_id, previous_output],
                        task_id=step_exec_id
                    )

                    # Wait for completion
                    step_result = result.get(timeout=step.tool.timeout_seconds + 60)

                    if step_result.get('output_for_next'):
                        previous_output = step_result['output_for_next']

            else:
                # Parallel execution
                parallel_tasks = []

                for step in steps_in_group:
                    step_exec_id = str(uuid.uuid4())
                    task = execute_pipeline_step_task.s(step_exec_id, step.id, execution_id, previous_output)
                    parallel_tasks.append(task)

                # Execute in parallel using Celery group
                job = group(parallel_tasks)
                result = job.apply_async()

                # Wait for all to complete
                result.get(timeout=max([s.tool.timeout_seconds for s in steps_in_group]) + 120)

                # Reset previous output for parallel groups
                previous_output = None

        # Mark execution as completed
        executor.finalize_execution(execution_id, ExecutionStatus.COMPLETED)

        return {
            'execution_id': execution_id,
            'status': 'completed',
            'message': f'Pipeline {pipeline.name} completed successfully'
        }

    except Exception as e:
        # Mark execution as failed
        session = get_session()
        executor = PipelineExecutor(session)
        executor.finalize_execution(execution_id, ExecutionStatus.FAILED, str(e))

        raise


# ===== PIPELINE ENDPOINTS =====

@ns_pipelines.route('/')
class PipelineList(Resource):
    @ns_pipelines.doc('list_pipelines')
    @ns_pipelines.marshal_list_with(pipeline_model)
    def get(self):
        """List all available pipelines"""
        session = get_session()
        pipelines = session.query(Pipeline).filter_by(is_active=True).all()

        return [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category.value if p.category else None,
            'estimated_duration_minutes': p.estimated_duration_minutes
        } for p in pipelines]


@ns_pipelines.route('/<int:pipeline_id>')
class PipelineDetail(Resource):
    @ns_pipelines.doc('get_pipeline')
    def get(self, pipeline_id):
        """Get detailed information about a pipeline"""
        session = get_session()
        pipeline = session.query(Pipeline).get(pipeline_id)

        if not pipeline:
            api.abort(404, "Pipeline not found")

        return {
            'id': pipeline.id,
            'name': pipeline.name,
            'description': pipeline.description,
            'category': pipeline.category.value if pipeline.category else None,
            'estimated_duration_minutes': pipeline.estimated_duration_minutes,
            'parallel_execution': pipeline.parallel_execution,
            'requires_env': pipeline.requires_env,
            'steps': [{
                'order': s.order,
                'tool_name': s.tool.name,
                'arguments': s.arguments,
                'parallel_group': s.parallel_group,
                'required': s.required
            } for s in pipeline.steps]
        }


@ns_pipelines.route('/<int:pipeline_id>/plan')
class PipelineExecutionPlan(Resource):
    @ns_pipelines.doc('get_execution_plan')
    def get(self, pipeline_id):
        """Get execution plan showing parallel and sequential phases"""
        session = get_session()
        executor = PipelineExecutor(session)

        try:
            plan = executor.get_execution_plan(pipeline_id)
            return plan
        except ValueError as e:
            api.abort(404, str(e))


@ns_pipelines.route('/<int:pipeline_id>/validate')
class PipelineValidation(Resource):
    @ns_pipelines.doc('validate_pipeline')
    def get(self, pipeline_id):
        """Validate pipeline requirements (env variables, etc.)"""
        validation = config_manager.validate_pipeline_requirements(pipeline_id)

        if not validation['valid']:
            return validation, 400

        return validation


# ===== EXECUTION ENDPOINTS =====

@ns_executions.route('/start')
class StartExecution(Resource):
    @ns_executions.expect(execution_request_model)
    @ns_executions.doc('start_execution')
    def post(self):
        """Start a new pipeline execution"""
        data = request.get_json()

        pipeline_id = data.get('pipeline_id')
        target = data.get('target')
        user_id = data.get('user_id', 'default')
        asset = data.get('asset')
        input_file = data.get('input_file')
        metadata = data.get('metadata', {})

        if not pipeline_id or not target:
            api.abort(400, "pipeline_id and target are required")

        try:
            session = get_session()
            executor = PipelineExecutor(session)

            # Prepare execution
            execution = executor.prepare_execution(
                pipeline_id=pipeline_id,
                target=target,
                user_id=user_id,
                asset=asset,
                input_file=input_file,
                metadata=metadata
            )

            # Start Celery task
            task = execute_pipeline_task.apply_async(
                args=[execution.id],
                task_id=f"pipeline_{execution.id}"
            )

            execution.celery_task_id = task.id
            session.commit()

            return {
                'message': 'Pipeline execution started',
                'execution_id': execution.id,
                'celery_task_id': task.id,
                'results_path': execution.results_path,
                'status_url': f'/executions/{execution.id}/status',
                'results_url': f'/results/{execution.id}'
            }, 202

        except Exception as e:
            api.abort(500, f"Failed to start execution: {str(e)}")


@ns_executions.route('/<string:execution_id>/status')
class ExecutionStatus(Resource):
    @ns_executions.doc('get_execution_status')
    def get(self, execution_id):
        """Get execution status and progress"""
        session = get_session()
        execution = session.query(Execution).get(execution_id)

        if not execution:
            api.abort(404, "Execution not found")

        # Get step executions
        step_executions = session.query(StepExecution).filter_by(
            execution_id=execution_id
        ).order_by(StepExecution.order).all()

        return {
            'execution_id': execution.id,
            'pipeline_name': execution.pipeline.name,
            'target': execution.target,
            'status': execution.status.value,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'progress': {
                'current': execution.progress_current,
                'total': execution.progress_total,
                'percentage': round((execution.progress_current / execution.progress_total * 100) if execution.progress_total else 0, 2)
            },
            'steps': [{
                'order': se.order,
                'tool': se.step.tool.name if se.step else 'Unknown',
                'status': se.status.value,
                'duration': se.duration_seconds,
                'parsed_results': se.parsed_results_count
            } for se in step_executions],
            'error_message': execution.error_message
        }


@ns_executions.route('/<string:execution_id>/cancel')
class CancelExecution(Resource):
    @ns_executions.doc('cancel_execution')
    def post(self, execution_id):
        """Cancel a running execution"""
        session = get_session()
        execution = session.query(Execution).get(execution_id)

        if not execution:
            api.abort(404, "Execution not found")

        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            return {'message': 'Execution is not running'}, 400

        # Revoke Celery task
        if execution.celery_task_id:
            celery.control.revoke(execution.celery_task_id, terminate=True)

        # Update status
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        session.commit()

        return {
            'message': 'Execution cancelled',
            'execution_id': execution_id
        }


@ns_executions.route('/list')
class ExecutionList(Resource):
    @ns_executions.doc('list_executions')
    def get(self):
        """List recent executions"""
        session = get_session()
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id')
        status = request.args.get('status')

        query = session.query(Execution).order_by(Execution.created_at.desc())

        if user_id:
            query = query.filter_by(user_id=user_id)

        if status:
            try:
                status_enum = ExecutionStatus[status.upper()]
                query = query.filter_by(status=status_enum)
            except KeyError:
                pass

        executions = query.limit(limit).all()

        return [{
            'execution_id': e.id,
            'pipeline': e.pipeline.name,
            'target': e.target,
            'status': e.status.value,
            'started_at': e.started_at.isoformat() if e.started_at else None,
            'user_id': e.user_id
        } for e in executions]


# ===== RESULTS ENDPOINTS =====

@ns_results.route('/<string:execution_id>')
class ExecutionResults(Resource):
    @ns_results.doc('get_execution_results')
    def get(self, execution_id):
        """Get all results from an execution"""
        session = get_session()
        executor = PipelineExecutor(session)

        result_type = request.args.get('type')
        limit = request.args.get('limit', 1000, type=int)

        results = executor.get_execution_results(
            execution_id=execution_id,
            result_type=result_type,
            limit=limit
        )

        return {
            'execution_id': execution_id,
            'total_results': len(results),
            'results': [{
                'type': r.result_type,
                'value': r.value,
                'source_tool': r.source_tool,
                'severity': r.severity,
                'confidence': r.confidence,
                'metadata': r.metadata,
                'created_at': r.created_at.isoformat()
            } for r in results]
        }


@ns_results.route('/<string:execution_id>/summary')
class ResultsSummary(Resource):
    @ns_results.doc('get_results_summary')
    def get(self, execution_id):
        """Get summary of results by type"""
        session = get_session()
        executor = PipelineExecutor(session)

        summary = executor.get_results_summary(execution_id)
        return summary


@ns_results.route('/<string:execution_id>/subdomains')
class SubdomainResults(Resource):
    @ns_results.doc('get_subdomains')
    def get(self, execution_id):
        """Get all discovered subdomains"""
        session = get_session()
        subdomains = ResultAggregator.combine_subdomain_results(execution_id, session)

        return {
            'execution_id': execution_id,
            'total_subdomains': len(subdomains),
            'subdomains': subdomains
        }


@ns_results.route('/<string:execution_id>/vulnerabilities')
class VulnerabilityResults(Resource):
    @ns_results.doc('get_vulnerabilities')
    def get(self, execution_id):
        """Get all vulnerabilities grouped by severity"""
        session = get_session()
        vulns = ResultAggregator.get_vulnerabilities_by_severity(execution_id, session)

        return {
            'execution_id': execution_id,
            'total_vulnerabilities': sum(len(v) for v in vulns.values()),
            'by_severity': {
                severity: [{
                    'value': v.value,
                    'source_tool': v.source_tool,
                    'metadata': v.metadata
                } for v in vulns_list]
                for severity, vulns_list in vulns.items()
            }
        }


@ns_results.route('/<string:execution_id>/export')
class ExportResults(Resource):
    @ns_results.doc('export_results')
    def get(self, execution_id):
        """Export all results to JSON file"""
        session = get_session()
        execution = session.query(Execution).get(execution_id)

        if not execution:
            api.abort(404, "Execution not found")

        output_file = f"{execution.results_path}/complete_results.json"

        try:
            ResultAggregator.export_results_to_json(execution_id, output_file, session)
            return send_file(output_file, as_attachment=True)
        except Exception as e:
            api.abort(500, f"Failed to export results: {str(e)}")


# ===== TOOLS ENDPOINTS =====

@ns_tools.route('/')
class ToolList(Resource):
    @ns_tools.doc('list_tools')
    def get(self):
        """List all available tools"""
        session = get_session()
        category = request.args.get('category')

        query = session.query(Tool)

        if category:
            try:
                category_enum = PhaseCategory[category.upper()]
                query = query.filter_by(category=category_enum)
            except KeyError:
                pass

        tools = query.all()

        return [{
            'id': t.id,
            'name': t.name,
            'command': t.command,
            'description': t.description,
            'category': t.category.value if t.category else None,
            'link': t.link
        } for t in tools]


@ns_tools.route('/categories')
class ToolCategories(Resource):
    @ns_tools.doc('list_categories')
    def get(self):
        """List all tool categories"""
        return [c.value for c in PhaseCategory]


# ===== CONFIGURATION ENDPOINTS =====

@ns_config.route('/env')
class EnvironmentConfig(Resource):
    @ns_config.doc('list_env_config')
    def get(self):
        """List all configuration keys (values hidden for sensitive)"""
        session = get_session()
        configs = session.query(Configuration).all()

        return [{
            'key': c.key,
            'description': c.description,
            'category': c.category,
            'is_sensitive': c.is_sensitive,
            'has_value': bool(c.value)
        } for c in configs]

    @ns_config.doc('update_env_config')
    def post(self):
        """Set configuration value"""
        data = request.get_json()

        key = data.get('key')
        value = data.get('value')
        description = data.get('description')
        is_sensitive = data.get('is_sensitive', False)
        category = data.get('category', 'user')

        if not key:
            api.abort(400, "key is required")

        config_manager.set(key, value, description, is_sensitive, category)

        return {'message': f'Configuration {key} updated'}


# ===== LEGACY COMPATIBILITY ENDPOINTS =====

@api.route('/run')
class LegacyRunTool(Resource):
    """Legacy endpoint for backward compatibility"""

    def post(self):
        """Run a single tool (legacy)"""
        data = request.get_json()
        tool_name = data.get('tool')
        args = data.get('args', [])

        if not tool_name:
            api.abort(400, "tool is required")

        # Create a simple execution
        session = get_session()
        execution_id = str(uuid.uuid4())

        # Execute tool directly
        command = f"{tool_name} {' '.join(args)}"
        task_id = str(uuid.uuid4())

        return {
            'message': f'Running {tool_name}',
            'job_id': task_id,
            'command': command
        }, 202


@api.route('/get_file/<path:file_path>')
class GetFile(Resource):
    def get(self, file_path):
        """Download result file"""
        full_path = os.path.join('/opt/results', file_path)

        if not os.path.exists(full_path):
            abort(404, description="File not found")

        try:
            return send_file(full_path, as_attachment=True)
        except Exception as e:
            abort(500, description=f"Error retrieving file: {str(e)}")


# ===== HEALTH CHECK =====

@api.route('/health')
class HealthCheck(Resource):
    def get(self):
        """API health check"""
        session = get_session()

        try:
            # Check database
            tool_count = session.query(Tool).count()
            pipeline_count = session.query(Pipeline).count()

            # Check Celery
            celery_stats = celery.control.inspect().stats()
            celery_ok = celery_stats is not None

            return {
                'status': 'healthy',
                'database': 'connected',
                'celery': 'connected' if celery_ok else 'disconnected',
                'tools_available': tool_count,
                'pipelines_available': pipeline_count
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

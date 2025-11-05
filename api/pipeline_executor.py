"""
Advanced pipeline execution engine with parallel execution support
Handles complex workflows, dependencies, and result aggregation
"""
import subprocess
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from celery import group, chord, chain
from sqlalchemy.orm import Session

from models import (
    Pipeline, PipelineStep, Execution, StepExecution, Result,
    ExecutionStatus, get_session
)
from result_parsers import get_parser


class PipelineExecutor:
    """
    Orchestrates pipeline execution with support for:
    - Parallel execution of independent steps
    - Sequential execution with dependencies
    - Result aggregation and parsing
    - Error handling and recovery
    """

    def __init__(self, session: Session = None):
        self.session = session or get_session()

    def prepare_execution(
        self,
        pipeline_id: int,
        target: str,
        user_id: str = "default",
        asset: str = None,
        input_file: str = None,
        metadata: Dict[str, Any] = None
    ) -> Execution:
        """
        Prepare execution record and directory structure
        """
        # Get pipeline
        pipeline = self.session.query(Pipeline).get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        if not pipeline.is_active:
            raise ValueError(f"Pipeline {pipeline.name} is not active")

        # Create execution ID
        execution_id = str(uuid.uuid4())

        # Create results directory
        asset_name = asset or target.replace('https://', '').replace('http://', '').replace('/', '_')
        results_path = f"/opt/results/{user_id}/{target}/{asset_name}/{execution_id}"
        os.makedirs(results_path, exist_ok=True)

        # Create execution record
        execution = Execution(
            id=execution_id,
            pipeline_id=pipeline_id,
            user_id=user_id,
            target=target,
            asset=asset_name,
            status=ExecutionStatus.PENDING,
            results_path=results_path,
            progress_total=len(pipeline.steps),
            metadata=metadata or {}
        )

        self.session.add(execution)
        self.session.commit()

        return execution

    def build_command(
        self,
        step: PipelineStep,
        execution: Execution,
        input_file: str = None
    ) -> str:
        """
        Build command with variable substitution
        """
        command = step.tool.command
        arguments = step.arguments or ""

        # Variable substitution
        replacements = {
            '{target}': execution.target,
            '{asset}': execution.asset,
            '{userId}': execution.user_id,
            '{user_id}': execution.user_id,
            '{results_path}': execution.results_path,
            '{input_file}': input_file or f"{execution.results_path}/input.txt",
            '{execution_id}': execution.id
        }

        for var, value in replacements.items():
            arguments = arguments.replace(var, value)
            command = command.replace(var, value)

        # Build full command
        full_command = f"{command} {arguments}"

        return full_command.strip()

    def execute_step(
        self,
        step_execution_id: str,
        step_id: int,
        execution_id: str,
        input_data: str = None,
        input_file: str = None
    ) -> Dict[str, Any]:
        """
        Execute a single pipeline step
        """
        try:
            # Get objects
            step = self.session.query(PipelineStep).get(step_id)
            execution = self.session.query(Execution).get(execution_id)

            if not step or not execution:
                raise ValueError("Step or Execution not found")

            # Update step execution status
            step_exec = StepExecution(
                id=step_execution_id,
                execution_id=execution_id,
                step_id=step_id,
                order=step.order,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            self.session.add(step_exec)
            self.session.commit()

            # Build command
            command = self.build_command(step, execution, input_file)
            step_exec.command_executed = command
            self.session.commit()

            # Execute command
            start_time = datetime.utcnow()

            if step.tool.supports_stdin and input_data:
                # Pass input via stdin
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                    timeout=step.tool.timeout_seconds
                )
                stdout, stderr = process.communicate(input=input_data)
                exit_code = process.returncode
            else:
                # Regular execution
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                    timeout=step.tool.timeout_seconds
                )
                stdout = result.stdout
                stderr = result.stderr
                exit_code = result.returncode

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Update step execution
            step_exec.stdout = stdout
            step_exec.stderr = stderr
            step_exec.exit_code = exit_code
            step_exec.completed_at = end_time
            step_exec.duration_seconds = duration

            # Check if step failed
            if exit_code != 0 and step.required:
                step_exec.status = ExecutionStatus.FAILED
                step_exec.error_message = f"Command failed with exit code {exit_code}: {stderr[:500]}"
                self.session.commit()
                raise Exception(step_exec.error_message)

            # Parse results if configured
            parsed_results = []
            if step.parse_output:
                output_file = self._extract_output_file(command)
                parser = get_parser(step.tool.name)
                parsed_results = parser.parse(stdout, output_file)

                # Save parsed results to database
                for result_data in parsed_results:
                    result = Result(
                        execution_id=execution_id,
                        step_execution_id=step_execution_id,
                        **result_data
                    )
                    self.session.add(result)

                step_exec.parsed_results_count = len(parsed_results)

            # Update status to completed
            step_exec.status = ExecutionStatus.COMPLETED
            self.session.commit()

            # Update execution progress
            completed_steps = self.session.query(StepExecution).filter(
                StepExecution.execution_id == execution_id,
                StepExecution.status == ExecutionStatus.COMPLETED
            ).count()

            execution.progress_current = completed_steps
            self.session.commit()

            return {
                'step_execution_id': step_execution_id,
                'status': 'completed',
                'exit_code': exit_code,
                'duration': duration,
                'parsed_results_count': len(parsed_results),
                'stdout': stdout,
                'stderr': stderr,
                'output_for_next': stdout if step.pass_to_next else None
            }

        except subprocess.TimeoutExpired:
            step_exec.status = ExecutionStatus.FAILED
            step_exec.error_message = f"Command timed out after {step.tool.timeout_seconds} seconds"
            self.session.commit()
            raise

        except Exception as e:
            if 'step_exec' in locals():
                step_exec.status = ExecutionStatus.FAILED
                step_exec.error_message = str(e)
                self.session.commit()
            raise

    def _extract_output_file(self, command: str) -> Optional[str]:
        """Extract output file path from command"""
        # Look for common output flags: -o, -output, >, >>
        patterns = [
            r'-o\s+([^\s]+)',
            r'--output[= ]([^\s]+)',
            r'>\s*([^\s|&]+)',
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, command)
            if match:
                return match.group(1)

        return None

    def organize_steps_by_groups(self, steps: List[PipelineStep]) -> Dict[int, List[PipelineStep]]:
        """
        Organize steps by parallel groups and order
        Steps with same parallel_group run in parallel
        Steps with different groups or None run sequentially
        """
        groups = {}

        for step in sorted(steps, key=lambda x: x.order):
            group_key = step.parallel_group if step.parallel_group is not None else f"seq_{step.order}"

            if group_key not in groups:
                groups[group_key] = []

            groups[group_key].append(step)

        return groups

    def get_execution_plan(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Generate execution plan showing parallel and sequential steps
        """
        pipeline = self.session.query(Pipeline).get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        groups = self.organize_steps_by_groups(pipeline.steps)

        plan = {
            'pipeline_name': pipeline.name,
            'total_steps': len(pipeline.steps),
            'execution_phases': []
        }

        for group_key in sorted(groups.keys(), key=lambda x: (isinstance(x, str), x)):
            steps_in_group = groups[group_key]

            phase = {
                'group': group_key,
                'parallel': len(steps_in_group) > 1 or (steps_in_group[0].parallel_group is not None),
                'steps': [
                    {
                        'order': s.order,
                        'tool': s.tool.name,
                        'arguments': s.arguments,
                        'required': s.required
                    }
                    for s in steps_in_group
                ]
            }

            plan['execution_phases'].append(phase)

        return plan

    def execute_pipeline(
        self,
        execution_id: str,
        celery_app=None
    ) -> str:
        """
        Execute entire pipeline with parallel execution support
        Returns celery task ID
        """
        execution = self.session.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        pipeline = execution.pipeline

        # Update status
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        self.session.commit()

        # Organize steps by parallel groups
        groups = self.organize_steps_by_groups(pipeline.steps)

        # Build Celery workflow
        # For now, return execution_id - actual Celery integration in server.py
        return execution_id

    def finalize_execution(self, execution_id: str, status: ExecutionStatus, error_message: str = None):
        """Mark execution as completed or failed"""
        execution = self.session.query(Execution).get(execution_id)
        if execution:
            execution.status = status
            execution.completed_at = datetime.utcnow()
            if error_message:
                execution.error_message = error_message
            self.session.commit()

    def get_execution_results(
        self,
        execution_id: str,
        result_type: str = None,
        limit: int = 1000
    ) -> List[Result]:
        """
        Get parsed results from execution
        """
        query = self.session.query(Result).filter(
            Result.execution_id == execution_id
        )

        if result_type:
            query = query.filter(Result.result_type == result_type)

        query = query.order_by(Result.created_at.desc()).limit(limit)

        return query.all()

    def get_results_summary(self, execution_id: str) -> Dict[str, Any]:
        """
        Get summary of results by type
        """
        from sqlalchemy import func

        results = self.session.query(
            Result.result_type,
            func.count(Result.id).label('count')
        ).filter(
            Result.execution_id == execution_id
        ).group_by(Result.result_type).all()

        summary = {
            'execution_id': execution_id,
            'total_results': sum([r.count for r in results]),
            'by_type': {r.result_type: r.count for r in results}
        }

        return summary

    def cleanup_old_executions(self, days_old: int = 30):
        """
        Cleanup old execution data
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        old_executions = self.session.query(Execution).filter(
            Execution.created_at < cutoff_date,
            Execution.status.in_([ExecutionStatus.COMPLETED, ExecutionStatus.FAILED])
        ).all()

        for execution in old_executions:
            # Delete results directory
            if execution.results_path and os.path.exists(execution.results_path):
                import shutil
                try:
                    shutil.rmtree(execution.results_path)
                except:
                    pass

            # Delete from database
            self.session.delete(execution)

        self.session.commit()

        return len(old_executions)


class ResultAggregator:
    """
    Aggregate and combine results from multiple steps
    """

    @staticmethod
    def combine_subdomain_results(execution_id: str, session: Session = None) -> List[str]:
        """Combine all unique subdomains from execution"""
        session = session or get_session()

        results = session.query(Result).filter(
            Result.execution_id == execution_id,
            Result.result_type == 'subdomain'
        ).all()

        subdomains = list(set([r.value for r in results]))
        return sorted(subdomains)

    @staticmethod
    def get_vulnerabilities_by_severity(execution_id: str, session: Session = None) -> Dict[str, List[Result]]:
        """Group vulnerabilities by severity"""
        session = session or get_session()

        results = session.query(Result).filter(
            Result.execution_id == execution_id,
            Result.result_type == 'vulnerability'
        ).all()

        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

        for result in results:
            severity = result.severity or 'info'
            if severity in by_severity:
                by_severity[severity].append(result)

        return by_severity

    @staticmethod
    def export_results_to_json(execution_id: str, output_file: str, session: Session = None):
        """Export all results to JSON file"""
        import json

        session = session or get_session()

        execution = session.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        results = session.query(Result).filter(
            Result.execution_id == execution_id
        ).all()

        export_data = {
            'execution_id': execution_id,
            'pipeline': execution.pipeline.name,
            'target': execution.target,
            'asset': execution.asset,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'status': execution.status.value,
            'total_results': len(results),
            'results': [
                {
                    'type': r.result_type,
                    'value': r.value,
                    'source_tool': r.source_tool,
                    'severity': r.severity,
                    'confidence': r.confidence,
                    'metadata': r.metadata,
                    'created_at': r.created_at.isoformat()
                }
                for r in results
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        return output_file

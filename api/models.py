"""
Database models for LemonDocker reconnaissance pipelines
"""
from sqlalchemy import create_engine, Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class PhaseCategory(enum.Enum):
    """Categories for reconnaissance phases"""
    SUBDOMAIN_ENUMERATION = "SUBDOMAIN_ENUMERATION"
    ACTIVE_VERIFICATION = "ACTIVE_VERIFICATION"
    SPIDERING = "SPIDERING"
    JAVASCRIPT_ANALYSIS = "JAVASCRIPT_ANALYSIS"
    PORT_SCANNING = "PORT_SCANNING"
    FINGERPRINTING = "FINGERPRINTING"
    VULNERABILITY_SCANNING = "VULNERABILITY_SCANNING"
    SCREENSHOT = "SCREENSHOT"
    BRUTEFORCING = "BRUTEFORCING"
    OSINT = "OSINT"
    GIT_ANALYSIS = "GIT_ANALYSIS"
    CLOUD_DISCOVERY = "CLOUD_DISCOVERY"
    SUBDOMAIN_TAKEOVER = "SUBDOMAIN_TAKEOVER"
    HOST_DISCOVERY = "HOST_DISCOVERY"
    UTILITY = "UTILITY"


class ExecutionStatus(enum.Enum):
    """Status of pipeline/step execution"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Tool(Base):
    """Security tools available for execution"""
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    command = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(PhaseCategory), nullable=False, index=True)
    link = Column(String(500))
    docker_image = Column(String(200))  # Optional docker image if tool needs specific container
    requires_env = Column(JSON)  # List of env variables required
    output_format = Column(String(50))  # json, txt, xml, etc.
    supports_stdin = Column(Boolean, default=False)
    supports_list_input = Column(Boolean, default=False)
    parallel_capable = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=3600)  # Default 1 hour timeout
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pipeline_steps = relationship("PipelineStep", back_populates="tool", cascade="all, delete-orphan")


class Pipeline(Base):
    """Reconnaissance pipelines composed of multiple steps"""
    __tablename__ = 'pipelines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(PhaseCategory), index=True)
    is_active = Column(Boolean, default=True)
    requires_env = Column(JSON)  # List of required env variables
    estimated_duration_minutes = Column(Integer)
    parallel_execution = Column(Boolean, default=False)  # Can steps run in parallel?
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("PipelineStep", back_populates="pipeline",
                        cascade="all, delete-orphan", order_by="PipelineStep.order")
    executions = relationship("Execution", back_populates="pipeline", cascade="all, delete-orphan")


class PipelineStep(Base):
    """Individual steps within a pipeline"""
    __tablename__ = 'pipeline_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'), nullable=False, index=True)
    tool_id = Column(Integer, ForeignKey('tools.id'), nullable=False, index=True)
    order = Column(Integer, nullable=False)  # Execution order
    arguments = Column(Text)  # Template arguments with placeholders like {target}, {userId}, {asset}
    depends_on_step = Column(Integer, ForeignKey('pipeline_steps.id'))  # Dependency on previous step
    condition = Column(Text)  # Optional condition to execute this step
    parallel_group = Column(Integer)  # Steps with same group number run in parallel
    required = Column(Boolean, default=True)  # Continue if this step fails?
    output_path = Column(String(500))  # Where to save output
    parse_output = Column(Boolean, default=True)  # Should output be parsed?
    pass_to_next = Column(Boolean, default=False)  # Pass output to next step via stdin?
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pipeline = relationship("Pipeline", back_populates="steps")
    tool = relationship("Tool", back_populates="pipeline_steps")
    step_executions = relationship("StepExecution", back_populates="step", cascade="all, delete-orphan")


class Execution(Base):
    """Pipeline execution instances"""
    __tablename__ = 'executions'

    id = Column(String(100), primary_key=True)  # UUID from Celery
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'), nullable=False, index=True)
    user_id = Column(String(100), index=True)  # User who initiated
    target = Column(String(500), nullable=False)  # Target domain/IP
    asset = Column(String(500))  # Specific asset being scanned
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    celery_task_id = Column(String(100), index=True)  # Main celery task ID
    celery_group_id = Column(String(100))  # Celery group/chord ID if parallel
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer)
    results_path = Column(String(1000))  # Base path for results
    metadata = Column(JSON)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    pipeline = relationship("Pipeline", back_populates="executions")
    step_executions = relationship("StepExecution", back_populates="execution",
                                  cascade="all, delete-orphan", order_by="StepExecution.order")
    results = relationship("Result", back_populates="execution", cascade="all, delete-orphan")


class StepExecution(Base):
    """Individual step execution tracking"""
    __tablename__ = 'step_executions'

    id = Column(String(100), primary_key=True)  # UUID from Celery
    execution_id = Column(String(100), ForeignKey('executions.id'), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey('pipeline_steps.id'), nullable=False)
    order = Column(Integer, nullable=False)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    celery_task_id = Column(String(100), index=True)
    command_executed = Column(Text)  # Actual command that was run
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    exit_code = Column(Integer)
    stdout = Column(Text)
    stderr = Column(Text)
    output_file = Column(String(1000))
    parsed_results_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("Execution", back_populates="step_executions")
    step = relationship("PipelineStep", back_populates="step_executions")


class Result(Base):
    """Parsed and structured results from executions"""
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(100), ForeignKey('executions.id'), nullable=False, index=True)
    step_execution_id = Column(String(100), ForeignKey('step_executions.id'), index=True)
    result_type = Column(String(100), index=True)  # subdomain, url, port, vulnerability, etc.
    value = Column(Text, nullable=False, index=True)  # Main value (domain, URL, etc.)
    metadata = Column(JSON)  # Additional structured data
    severity = Column(String(50))  # For vulnerabilities: critical, high, medium, low, info
    confidence = Column(Float)  # Confidence score 0-1
    source_tool = Column(String(100), index=True)  # Tool that found this
    verified = Column(Boolean, default=False)
    false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    execution = relationship("Execution", back_populates="results")


class Configuration(Base):
    """Environment and tool configurations"""
    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(200), unique=True, nullable=False, index=True)
    value = Column(Text)  # Encrypted sensitive values
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)  # Encrypt this value
    category = Column(String(100), index=True)  # api_keys, tool_config, system, etc.
    required_for_tools = Column(JSON)  # List of tools that need this config
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database initialization
def init_db(database_url='sqlite:////opt/results/pipelines.db'):
    """Initialize database with all tables"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(database_url='sqlite:////opt/results/pipelines.db'):
    """Get database session"""
    engine = create_engine(database_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()

"""Tests for architecture diagrams."""

import pytest
from pathlib import Path
import yaml
import json
from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

def test_diagrams_structure():
    """Test diagrams directory structure."""
    diagrams_dir = Path("diagrams")
    assert diagrams_dir.exists(), "Missing diagrams directory"
    
    required_dirs = [
        "system",
        "data",
        "infrastructure"
    ]
    
    for dir_name in required_dirs:
        assert (diagrams_dir / dir_name).exists(), f"Missing directory: {dir_name}"

def test_system_diagrams():
    """Test system diagrams."""
    system_dir = Path("diagrams/system")
    assert system_dir.exists(), "Missing system diagrams directory"
    
    required_files = [
        "component.puml",
        "sequence.puml",
        "deployment.puml"
    ]
    
    for file in required_files:
        assert (system_dir / file).exists(), f"Missing file: {file}"

def test_data_diagrams():
    """Test data diagrams."""
    data_dir = Path("diagrams/data")
    assert data_dir.exists(), "Missing data diagrams directory"
    
    required_files = [
        "er.puml",
        "data_model.puml",
        "data_flow.puml"
    ]
    
    for file in required_files:
        assert (data_dir / file).exists(), f"Missing file: {file}"

def test_infrastructure_diagrams():
    """Test infrastructure diagrams."""
    infra_dir = Path("diagrams/infrastructure")
    assert infra_dir.exists(), "Missing infrastructure diagrams directory"
    
    required_files = [
        "network.puml",
        "security.puml",
        "dr.puml"
    ]
    
    for file in required_files:
        assert (infra_dir / file).exists(), f"Missing file: {file}"

def test_component_diagram():
    """Test component diagram."""
    component_file = Path("diagrams/system/component.puml")
    assert component_file.exists(), "Missing component diagram file"
    
    with open(component_file) as f:
        content = f.read()
    
    required_components = [
        "Frontend",
        "Backend",
        "Database",
        "AI Engine"
    ]
    
    for component in required_components:
        assert component in content, f"Missing component: {component}"

def test_sequence_diagram():
    """Test sequence diagram."""
    sequence_file = Path("diagrams/system/sequence.puml")
    assert sequence_file.exists(), "Missing sequence diagram file"
    
    with open(sequence_file) as f:
        content = f.read()
    
    required_sequences = [
        "User Request",
        "AI Processing",
        "Response"
    ]
    
    for sequence in required_sequences:
        assert sequence in content, f"Missing sequence: {sequence}"

def test_deployment_diagram():
    """Test deployment diagram."""
    deployment_file = Path("diagrams/system/deployment.puml")
    assert deployment_file.exists(), "Missing deployment diagram file"
    
    with open(deployment_file) as f:
        content = f.read()
    
    required_nodes = [
        "Web Server",
        "Application Server",
        "Database Server",
        "AI Server"
    ]
    
    for node in required_nodes:
        assert node in content, f"Missing node: {node}"

def test_er_diagram():
    """Test ER diagram."""
    er_file = Path("diagrams/data/er.puml")
    assert er_file.exists(), "Missing ER diagram file"
    
    with open(er_file) as f:
        content = f.read()
    
    required_entities = [
        "User",
        "Project",
        "Document",
        "Model"
    ]
    
    for entity in required_entities:
        assert entity in content, f"Missing entity: {entity}"

def test_data_model_diagram():
    """Test data model diagram."""
    model_file = Path("diagrams/data/data_model.puml")
    assert model_file.exists(), "Missing data model diagram file"
    
    with open(model_file) as f:
        content = f.read()
    
    required_models = [
        "User Model",
        "Project Model",
        "Document Model",
        "AI Model"
    ]
    
    for model in required_models:
        assert model in content, f"Missing model: {model}"

def test_data_flow_diagram():
    """Test data flow diagram."""
    flow_file = Path("diagrams/data/data_flow.puml")
    assert flow_file.exists(), "Missing data flow diagram file"
    
    with open(flow_file) as f:
        content = f.read()
    
    required_flows = [
        "User Input",
        "Data Processing",
        "AI Analysis",
        "Output"
    ]
    
    for flow in required_flows:
        assert flow in content, f"Missing flow: {flow}"

def test_network_diagram():
    """Test network diagram."""
    network_file = Path("diagrams/infrastructure/network.puml")
    assert network_file.exists(), "Missing network diagram file"
    
    with open(network_file) as f:
        content = f.read()
    
    required_components = [
        "Load Balancer",
        "Web Server",
        "Database",
        "Cache"
    ]
    
    for component in required_components:
        assert component in content, f"Missing component: {component}"

def test_security_diagram():
    """Test security diagram."""
    security_file = Path("diagrams/infrastructure/security.puml")
    assert security_file.exists(), "Missing security diagram file"
    
    with open(security_file) as f:
        content = f.read()
    
    required_components = [
        "Firewall",
        "VPN",
        "IDS",
        "WAF"
    ]
    
    for component in required_components:
        assert component in content, f"Missing component: {component}"

def test_dr_diagram():
    """Test disaster recovery diagram."""
    dr_file = Path("diagrams/infrastructure/dr.puml")
    assert dr_file.exists(), "Missing disaster recovery diagram file"
    
    with open(dr_file) as f:
        content = f.read()
    
    required_components = [
        "Primary Site",
        "Backup Site",
        "Replication",
        "Failover"
    ]
    
    for component in required_components:
        assert component in content, f"Missing component: {component}"

def test_diagram_utils():
    """Test diagram utilities."""
    utils_file = Path("diagrams/utils.py")
    assert utils_file.exists(), "Missing diagram utils file"
    
    with open(utils_file) as f:
        content = f.read()
    
    required_functions = [
        "generate_diagram",
        "validate_diagram",
        "export_diagram"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_diagram_config():
    """Test diagram configuration."""
    config_file = Path("diagrams/config.py")
    assert config_file.exists(), "Missing diagram config file"
    
    with open(config_file) as f:
        content = f.read()
    
    required_config = [
        "theme",
        "format",
        "output_dir"
    ]
    
    for config in required_config:
        assert config in content, f"Missing config: {config}" 
#!/usr/bin/env python3

import subprocess
import sys
import re
from typing import List, Dict
import argparse
from pathlib import Path

def run_command(command: List[str]) -> str:
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command {' '.join(command)}: {e}")
        sys.exit(1)

def get_node_list(partition: str) -> str:
    """Get the node list for a given Slurm partition."""
    nodelist = run_command(['sinfo', '-p', partition, '-h', '-o', '%N'])
    if not nodelist:
        print(f"Error: No nodes found in partition {partition}")
        sys.exit(1)
    return nodelist

def expand_node_list(nodelist: str) -> List[str]:
    """Expand the Slurm node notation into individual hostnames."""
    return run_command(['scontrol', 'show', 'hostnames', nodelist]).split('\n')

def get_node_info(node: str) -> Dict[str, str]:
    """Get detailed information about a specific node."""
    node_info = run_command(['scontrol', 'show', 'node', node, '-o'])
    
    # Extract relevant information using regex
    state_match = re.search(r'State=(\S+)', node_info)
    features_match = re.search(r'Features=(\S+)', node_info)
    cpus_match = re.search(r'CPUTot=(\d+)', node_info)
    memory_match = re.search(r'RealMemory=(\d+)', node_info)
    
    return {
        'state': state_match.group(1) if state_match else 'unknown',
        'features': features_match.group(1) if features_match else '',
        'cpus': cpus_match.group(1) if cpus_match else '0',
        'memory': memory_match.group(1) if memory_match else '0'
    }

def create_inventory(partition: str, output_file: str):
    """Create an Ansible inventory file from a Slurm partition."""
    # Get and expand node list
    nodelist = get_node_list(partition)
    nodes = expand_node_list(nodelist)
    
    # Create inventory file
    with open(output_file, 'w') as f:
        # Write header
        f.write("[slurm_nodes]\n")
        
        # Add each node with its properties
        for node in nodes:
            info = get_node_info(node)
            f.write(f"{node}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Generate Ansible inventory file from Slurm partition'
    )
    parser.add_argument('--partition', help='Slurm partition name')
    parser.add_argument(
        '--output', '-o',
        help='Output inventory file path',
        default=None
    )
    
    args = parser.parse_args()
    
    # Generate default output filename if not specified
    output_file = args.output or f"/fsx/ubuntu/matt/cluster_visualization/inventory_{args.partition}.ini"
    
    create_inventory(args.partition, output_file)
    print(f"Inventory file generated: {output_file}")

if __name__ == '__main__':
    main()
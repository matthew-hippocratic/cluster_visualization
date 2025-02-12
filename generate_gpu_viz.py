import csv
import os

def read_gpu_data(csv_path):
    data = []
    with open(csv_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if row:  # Skip empty rows
                node, model, gpus = row
                # Convert GPU string to list of integers
                gpu_list = [int(x) for x in gpus.strip('[]').split()]
                data.append({
                    'node': node,
                    'model': model,
                    'GPUs': gpu_list
                })
    return data

def generate_html(data, nodes):
    # Get unique nodes
    occupied_nodes = sorted(set(node['node'] for node in data))
    nodes = sorted(set(nodes + occupied_nodes))
    
    # Create GPU allocation lookup
    gpu_allocations = {}
    for node in nodes:
        gpu_allocations[node] = {}
        for i in range(8):  # 8 GPUs per node
            gpu_allocations[node][i] = None
            
    for item in data:
        node = item['node']
        model = item['model']
        for gpu in item['GPUs']:
            gpu_allocations[node][gpu] = model

    # Generate HTML
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>GPU Allocation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .node {
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .gpu-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .gpu {
            width: 100px;
            height: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            border-radius: 4px;
            padding: 5px;
        }
        .gpu.free {
            background-color: #22c55e;
            color: black;
        }
        .gpu.occupied {
            background-color: #dc2626;
        }
        .model-name {
            font-size: 12px;
            word-break: break-word;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>GPU Allocation</h1>
'''
    
    # Generate HTML for each node
    for node in nodes:
        html += f'''
    <div class="node">
        <h2>{node}</h2>
        <div class="gpu-container">
'''
        for gpu_num in range(8):
            model = gpu_allocations[node][gpu_num]
            status_class = 'occupied' if model else 'free'
            html += f'''
            <div class="gpu {status_class}">
                <div>GPU {gpu_num}</div>
'''
            if model:
                html += f'                <div class="model-name">{model}</div>\n'
            html += '            </div>\n'
            
        html += '''        </div>
    </div>
'''
    
    html += '''</body>
</html>'''
    
    return html

def main():
    # Read data from CSV
    data = read_gpu_data('/fsx/ubuntu/matt/cluster_visualization/gpu_usage_combined.csv')

    # Read nodes that might not have GPUs from the inventory_ml.inference.ini file
    nodes = []
    with open('/fsx/ubuntu/matt/cluster_visualization/inventory_ml.inference.ini', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('['):
                continue
            nodes.append(line.strip())
    
    # Generate HTML
    html_content = generate_html(data, nodes)
    
    # Write to file
    with open('gpu_allocation.html', 'w') as f:
        f.write(html_content)
    
    print(f"HTML file generated as 'gpu_allocation.html'")
    print(f"Absolute path: {os.path.abspath('gpu_allocation.html')}")

if __name__ == "__main__":
    main()
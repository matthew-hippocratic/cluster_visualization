# First create the inventory file from running the python script
source ~/venv/bin/activate
python /fsx/ubuntu/matt/cluster_visualization/create_inventory_file.py --partition ml.inference

# Then run the ansible playbook with the inventory file,
# passing in a base directory for CSV files (update the basedir as needed)
ansible-playbook -i /fsx/ubuntu/matt/cluster_visualization/inventory_ml.inference.ini \
  /fsx/ubuntu/matt/cluster_visualization/gpu_info_ansible.yaml \
  -f 100 --extra-vars "basedir=/fsx/ubuntu/matt/cluster_visualization"

# Then run the python script to create the html file
python /fsx/ubuntu/matt/cluster_visualization/generate_gpu_viz.py
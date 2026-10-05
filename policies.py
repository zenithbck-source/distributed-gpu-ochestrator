from nodes import nodes
from copy import deepcopy
from job_generator import generate_job

def splitting(jobs):
    # all_nodes[0] -> node-01, all_nodes[1] -> node-02 ...
    all_nodes = [[], []]

    for job in jobs:
        i = 0 if job['gpu_type'] == 'A100' else 1
        all_nodes[i].append(job)
    
    return all_nodes

    
def fcfs(job_list):
    #nodes_copy = deepcopy(nodes)
    total_jobs = len(job_list)
    jobs = splitting(job_list)
    schedule = [[], [], [], []]  # each list for one node
    time = 0
    completed = 0

    for i, node_jobs in enumerate(jobs):
        for job in node_jobs:
            job['total_ram_gb'] = job['cpu_cores'] * job['ram_gb_per_cpu']
        jobs[i] = sorted(node_jobs, key=lambda job: job['submit_time'])


    while completed < total_jobs:
        for i, node_jobs in enumerate(jobs):
            for job in node_jobs:
                    if job['state'] == 'S' and job['end_time'] <= time:
                        if job['node'] == (f"node{i*2}"):
                            nodes[i*2]['avail_gpu_count'] += job['gpu_count']
                            nodes[i*2]['avail_cpu_cores'] += job['cpu_cores']
                            nodes[i*2]['avail_ram_gb'] += job['total_ram_gb']

                            job['state'] = 'E'
                            schedule[i*2].append(job)
                        elif job['node'] == (f"node{i*2+1}"):
                            nodes[i*2+1]['avail_gpu_count'] += job['gpu_count']
                            nodes[i*2+1]['avail_cpu_cores'] += job['cpu_cores']
                            nodes[i*2+1]['avail_ram_gb'] += job['total_ram_gb']

                            job['state'] = 'E'
                            schedule[i*2+1].append(job)
                        completed += 1
                        
                    if job['state'] == 'Q' and job['submit_time'] <= time:
                        if job['gpu_count'] <= nodes[i*2]['avail_gpu_count'] and job['cpu_cores'] <= nodes[i*2]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes[i*2]['avail_ram_gb']:
                            job['start_time'] = time
                            job['end_time'] = time + job['runtime']
                            job['state'] = 'S'
                            job['node'] = (f'node{i*2}')

                            nodes[i*2]['avail_gpu_count'] -= job['gpu_count']
                            nodes[i*2]['avail_cpu_cores'] -= job['cpu_cores']
                            nodes[i*2]['avail_ram_gb'] -= job['total_ram_gb']
                            print(f"{job['node']} | {nodes[i*2]['avail_gpu_count']} GPU | {nodes[i*2]['avail_cpu_cores']} CPU | {nodes[i*2]['avail_ram_gb']} GB")

                        elif job['gpu_count'] <= nodes[i*2+1]['avail_gpu_count'] and job['cpu_cores'] <= nodes[i*2+1]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes[i*2+1]['avail_ram_gb']:
                            job['start_time'] = time
                            job['end_time'] = time + job['runtime']
                            job['state'] = 'S'
                            job['node'] = (f'node{i*2+1}')

                            nodes[i*2+1]['avail_gpu_count'] -= job['gpu_count']
                            nodes[i*2+1]['avail_cpu_cores'] -= job['cpu_cores']
                            nodes[i*2+1]['avail_ram_gb'] -= job['total_ram_gb']
                            print(f"{job['node']} | {nodes[i*2+1]['avail_gpu_count']} GPU | {nodes[i*2+1]['avail_cpu_cores']} CPU | {nodes[i*2+1]['avail_ram_gb']} GB")
        time += 1
        
        
    return schedule, jobs, time




if __name__ == "__main__":
    jobs = generate_job(100, 42)
    schedule, log, total_time = fcfs(jobs)

    keys_to_display = [
        "job_id",
        "node",
        "gpu_count",
        "cpu_cores",
        "ram_gb_per_cpu",
        "total_ram_gb",
        "submit_time",
        "start_time",
        "end_time",
        "runtime"
    ]
    print()
    for node in log:
        for job in node:
            print({key: job[key] for key in keys_to_display})
        print()
        

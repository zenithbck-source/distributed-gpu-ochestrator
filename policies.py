from nodes import nodes
from copy import deepcopy
from collections import deque
from job_generator import generate_job

# ===== UTILS =====
def splitting(jobs):
    # all_nodes[0] -> node-01, all_nodes[1] -> node-02 ...
    all_nodes = [[], []]

    for job in jobs:
        i = 0 if job['gpu_type'] == 'A100' else 1
        all_nodes[i].append(job)
    
    return all_nodes

def job_completed(index, job, nodes, schedule):
    nodes[index]['avail_gpu_count'] += job['gpu_count']
    nodes[index]['avail_cpu_cores'] += job['cpu_cores']
    nodes[index]['avail_ram_gb'] += job['total_ram_gb']

    job['state'] = 'E'
    schedule[index].append(job)

def job_started(index, job, nodes, time):
    job['start_time'] = time
    job['end_time'] = time + job['runtime']
    job['state'] = 'S'
    job['node'] = (f'node{index}')

    nodes[index]['avail_gpu_count'] -= job['gpu_count']
    nodes[index]['avail_cpu_cores'] -= job['cpu_cores']
    nodes[index]['avail_ram_gb'] -= job['total_ram_gb']


# ===== POLICIES =====    
def fcfs(job_list):
    nodes_copy = deepcopy(nodes)
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
                            job_completed(i*2, job, nodes_copy, schedule)

                        elif job['node'] == (f"node{i*2+1}"):
                            job_completed(i*2+1, job, nodes_copy, schedule)

                        completed += 1
                        
                    if job['state'] == 'Q' and job['submit_time'] <= time:
                        if job['gpu_count'] <= nodes_copy[i*2]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[i*2]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[i*2]['avail_ram_gb']:
                            job_started(i*2, job, nodes_copy, time)
                            print(f"{job['node']} | {nodes_copy[i*2]['avail_gpu_count']} GPU | {nodes_copy[i*2]['avail_cpu_cores']} CPU | {nodes_copy[i*2]['avail_ram_gb']} GB")
                            if nodes_copy[i*2]['avail_cpu_cores'] < 0 or nodes_copy[i*2]['avail_ram_gb'] < 0: print("^^^ WARNING: OVERBOOKING ^^^") 

                        elif job['gpu_count'] <= nodes_copy[i*2+1]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[i*2+1]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[i*2+1]['avail_ram_gb']:
                            job_started(i*2+1, job, nodes_copy, time)
                            print(f"{job['node']} | {nodes_copy[i*2+1]['avail_gpu_count']} GPU | {nodes_copy[i*2+1]['avail_cpu_cores']} CPU | {nodes_copy[i*2+1]['avail_ram_gb']} GB")
                            if nodes_copy[i*2+1]['avail_cpu_cores'] < 0 or nodes_copy[i*2+1]['avail_ram_gb'] < 0: print("^^^ WARNING: OVERBOOKING ^^^") 

        #print(f"\ntime: {time}")
        #print(f"node0 | {nodes[0]['avail_gpu_count']} GPU | {nodes[0]['avail_cpu_cores']} CPU | {nodes[0]['avail_ram_gb']} GB")
        #print(f"node1 | {nodes[1]['avail_gpu_count']} GPU | {nodes[1]['avail_cpu_cores']} CPU | {nodes[1]['avail_ram_gb']} GB")
        #print(f"node2 | {nodes[2]['avail_gpu_count']} GPU | {nodes[2]['avail_cpu_cores']} CPU | {nodes[2]['avail_ram_gb']} GB")
        #print(f"node3 | {nodes[3]['avail_gpu_count']} GPU | {nodes[3]['avail_cpu_cores']} CPU | {nodes[3]['avail_ram_gb']} GB")
        time += 1
        
    return schedule, jobs, time

def priority(job_list):
    nodes_copy = deepcopy(nodes)
    total_jobs = len(job_list)
    jobs = splitting(job_list)
    schedule = [[], [], [], []]  # each list for one node
    queue = deque()
    time = 0
    completed = 0

    for i, node_jobs in enumerate(jobs):
        for job in node_jobs:
            job['total_ram_gb'] = job['cpu_cores'] * job['ram_gb_per_cpu']
        jobs[i] = sorted(node_jobs, key=lambda job: job['submit_time'])

    while time < 100:
        for i, node_jobs in enumerate(jobs):
            for job in node_jobs:
                if job['submit_time'] == time:
                    queue.append(job)

        queue = deque(sorted(queue, key=lambda job: (-job['priority'], job['submit_time'])))
        
        time += 1

    return queue
    



if __name__ == "__main__":
    jobs = generate_job(10, 42)
    #schedule, log, total_time = fcfs(jobs)
    queue = priority(jobs)

    keys_to_display = [
        "job_id",
#        "node",
#        "gpu_count",
#        "cpu_cores",
#        "ram_gb_per_cpu",
#        "total_ram_gb",
        "submit_time",
#        "start_time",
#        "end_time",
#        "runtime",
        "priority"
    ]

    print()
    #for node in log:
    #    for job in node:
    #        print({key: job[key] for key in keys_to_display})
    #    print()

    for job in queue:
        print({key: job[key] for key in keys_to_display})
        

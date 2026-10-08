from nodes import nodes
from copy import deepcopy
from collections import deque
from job_generator import generate_job

# ===== UTILS =====
def splitting(jobs):
    all_nodes = [[], []]

    for job in jobs:
        i = 0 if job['gpu_type'] == 'A100' else 1
        all_nodes[i].append(job)
    
    return all_nodes

def job_preparation(jobs):
    jobs_copy = deepcopy(jobs)

    for job in jobs_copy:
        job['total_ram_gb'] = job['cpu_cores'] * job['ram_gb_per_cpu']

    return jobs_copy

def job_completed(index, job, nodes, schedule):
    nodes[index]['avail_gpu_count'] += job['gpu_count']
    nodes[index]['avail_cpu_cores'] += job['cpu_cores']
    nodes[index]['avail_ram_gb'] += job['total_ram_gb']

    job['state'] = 'F'
    schedule[index].append(job)

def job_started(index, job, nodes, time):
    job['start_time'] = time
    job['end_time'] = time + job['runtime']
    job['state'] = 'R'
    job['node'] = (f'node{index}')

    nodes[index]['avail_gpu_count'] -= job['gpu_count']
    nodes[index]['avail_cpu_cores'] -= job['cpu_cores']
    nodes[index]['avail_ram_gb'] -= job['total_ram_gb']


# ===== POLICIES =====    
def fcfs(job_list):
    nodes_copy = deepcopy(nodes)
    total_jobs = len(job_list)
    schedule = [[], [], [], []]  # each list for one node
    time = 0
    completed = 0


    jobs = job_preparation(job_list)
    jobs = splitting(jobs)  # Splits jobs into two lists, separating A100 and H100 jobs

    # Sorting jobs based on submission time
    for i, node_jobs in enumerate(jobs):
        jobs[i] = sorted(node_jobs, key=lambda job: job['submit_time'])

    while completed < total_jobs:
        for i, node_jobs in enumerate(jobs):
            for job in node_jobs:
                    # Freeing resources in the node when job completes
                    if job['state'] == 'R' and job['end_time'] <= time:
                        if job['node'] == (f"node{i*2}"):
                            job_completed(i*2, job, nodes_copy, schedule)
                        elif job['node'] == (f"node{i*2+1}"):
                            job_completed(i*2+1, job, nodes_copy, schedule)
                        completed += 1

                    # Looping through all jobs to begin jobs that have enough resources (GPU, CPU, RAM)
                    # Makes use of the index of the job (from enumerate) to split into nodes 0/1 or nodes 2/3
                    if job['state'] == 'Q' and job['submit_time'] <= time:
                        if job['gpu_count'] <= nodes_copy[i*2]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[i*2]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[i*2]['avail_ram_gb']:
                            job_started(i*2, job, nodes_copy, time)

                            # Checking resources at the node after each job starts
                            #print(f"{job['node']} | {nodes_copy[i*2]['avail_gpu_count']} GPU | {nodes_copy[i*2]['avail_cpu_cores']} CPU | {nodes_copy[i*2]['avail_ram_gb']} GB")
                            #if nodes_copy[i*2]['avail_cpu_cores'] < 0 or nodes_copy[i*2]['avail_ram_gb'] < 0: print("^^^ WARNING: OVERBOOKING ^^^") 

                        elif job['gpu_count'] <= nodes_copy[i*2+1]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[i*2+1]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[i*2+1]['avail_ram_gb']:
                            job_started(i*2+1, job, nodes_copy, time)

                            # Checking resources at the node after each job starts
                            #print(f"{job['node']} | {nodes_copy[i*2+1]['avail_gpu_count']} GPU | {nodes_copy[i*2+1]['avail_cpu_cores']} CPU | {nodes_copy[i*2+1]['avail_ram_gb']} GB")
                            #if nodes_copy[i*2+1]['avail_cpu_cores'] < 0 or nodes_copy[i*2+1]['avail_ram_gb'] < 0: print("^^^ WARNING: OVERBOOKING ^^^") 

        # Checking resources of each node at every timestep
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
    log = []
    schedule = [[], [], [], []]  # each list for one node
    queueA = deque()
    queueH = deque()
    jobs_removingA = []
    jobs_removingH = []
    time = 0
    completed = 0


    jobs = job_preparation(job_list)
    
    while completed < total_jobs:
        # Freeing resources in the node when job completes
        for job in jobs:
            if job['state'] == 'R' and job['end_time'] <= time:
                if job['node'] == 'node0': job_completed(0, job, nodes_copy, schedule)
                elif job['node'] == 'node1': job_completed(1, job, nodes_copy, schedule)
                elif job['node'] == 'node2': job_completed(2, job, nodes_copy, schedule)
                elif job['node'] == 'node3': job_completed(3, job, nodes_copy, schedule)
                completed += 1

        # Splitting jobs, based on GPU type, into respective queue
        for job in jobs:
            if job['submit_time'] == time:
                job['state'] = 'Q'
                queueA.append(job) if job['gpu_type'] == 'A100' else queueH.append(job)

        # Sorting queues based on priority (descending), then submission time (ascending)
        queueA = deque(sorted(queueA, key=lambda job: (-job['priority'], job['submit_time'])))
        queueH = deque(sorted(queueH, key=lambda job: (-job['priority'], job['submit_time'])))

        # Looping through entire queue for A100 to begin jobs that have enough resources (GPU, CPU, RAM)
        for job in queueA.copy():
            if job['gpu_count'] <= nodes_copy[0]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[0]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[0]['avail_ram_gb']:
                job_started(0, job, nodes_copy, time)
                jobs_removingA.append(job)
            elif job['gpu_count'] <= nodes_copy[1]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[1]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[1]['avail_ram_gb']:
                job_started(1, job, nodes_copy, time)
                jobs_removingA.append(job)

        # Looping through entire queue for H100 to begin jobs that have enough resources (GPU, CPU, RAM)
        for job in queueH.copy():
            if job['gpu_count'] <= nodes_copy[2]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[2]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[2]['avail_ram_gb']:
                job_started(2, job, nodes_copy, time)
                jobs_removingH.append(job)
            elif job['gpu_count'] <= nodes_copy[3]['avail_gpu_count'] and job['cpu_cores'] <= nodes_copy[3]['avail_cpu_cores'] and job['total_ram_gb'] <= nodes_copy[3]['avail_ram_gb']:
                job_started(3, job, nodes_copy, time)
                jobs_removingH.append(job)

        # Removing started A100 jobs from queue and adding to the shared log
        for job in jobs_removingA:
            queueA.remove(job)
            log.append(job)

        # Removing started H100 jobs from queue and adding to the shared log
        for job in jobs_removingH:
            queueH.remove(job)
            log.append(job)

        jobs_removingA = []
        jobs_removingH = []

        time += 1

    return queueA, queueH, log
    



if __name__ == "__main__":
    jobs = generate_job(100, 42)
    schedule, log_fcfs, total_time = fcfs(jobs)
    queueA, queueH, log_priority = priority(jobs)

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
        "runtime",
        "priority"
    ]

    # ===== Check for FCFS =====
    print("===== FCFS POLICY =====")
    print("\nLog for Node 0 and Node 1:")
    for job in log_fcfs[0]:
        print({key: job[key] for key in keys_to_display})

    print("\nLog for Node 2 and Node 3:")
    for job in log_fcfs[1]:
        print({key: job[key] for key in keys_to_display})


    print("\n\n\n")

    # ===== Checks For Priority =====
    print("===== PRIORITY POLICY =====")
    print("\nLog for Node 0 and Node 1:")
    for job in log_priority:
        if job['node'] == 'node0' or job['node'] == 'node1': print({key: job[key] for key in keys_to_display})

    print("\nLog for Node 2 and Node 3:")
    for job in log_priority:
        if job['node'] == 'node2' or job['node'] == 'node3': print({key: job[key] for key in keys_to_display})
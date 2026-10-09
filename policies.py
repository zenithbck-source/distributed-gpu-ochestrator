from nodes import nodes
from copy import deepcopy
from collections import deque
from queue import Queue
from job_generator import generate_job

# ===== UTILS =====
node_groups = {
    'A100': [0, 1],
    'H100': [2, 3]
}

def job_preparation(jobs):
    jobs_copy = deepcopy(jobs)

    for job in jobs_copy:
        job['total_ram_gb'] = job['cpu_cores'] * job['ram_gb_per_cpu']

    return jobs_copy

def job_completed(index, job, nodes):
    nodes[index]['avail_gpu_count'] += job['gpu_count']
    nodes[index]['avail_cpu_cores'] += job['cpu_cores']
    nodes[index]['avail_ram_gb'] += job['total_ram_gb']

    job['state'] = 'F'

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
    log = []
    queueA = Queue()
    queueH = Queue()
    time = 0
    completed = 0
    schedulingA = True
    schedulingH = True
    job_scheduled = False

    jobs = job_preparation(job_list)
    jobs.sort(key=lambda job: job['submit_time'])

    while completed < total_jobs:
        for job in log:
            if job['state'] == 'R' and job['end_time'] <= time:
                node_index = int(job['node'].replace("node", ""))
                job_completed(node_index, job, nodes_copy)
                completed += 1

        # Splitting jobs, based on GPU type, into respective queue
        for job in jobs:
            if job['submit_time'] == time:
                job['state'] = 'Q'
                queueA.put(job) if job['gpu_type'] == 'A100' else queueH.put(job)

        schedulingA = True
        schedulingH = True

        while schedulingA:
            if queueA.empty(): break
            with queueA.mutex:
                current_job = queueA.queue[0]
            job_scheduled = False
            for node_index in node_groups['A100']:
                node = nodes_copy[node_index]
                if current_job['gpu_count'] <= node['avail_gpu_count'] and current_job['cpu_cores'] <= node['avail_cpu_cores'] and current_job['total_ram_gb'] <= node['avail_ram_gb']:
                    job_started(node_index, current_job, nodes_copy, time)
                    queueA.get()
                    log.append(current_job)
                    job_scheduled = True
                    break
            if not job_scheduled:
                schedulingA = False

        while schedulingH:
            if queueH.empty(): break
            with queueH.mutex:
                current_job = queueH.queue[0]
            job_scheduled = False
            for node_index in node_groups['H100']:
                node = nodes_copy[node_index]
                if current_job['gpu_count'] <= node['avail_gpu_count'] and current_job['cpu_cores'] <= node['avail_cpu_cores'] and current_job['total_ram_gb'] <= node['avail_ram_gb']:
                    job_started(node_index, current_job, nodes_copy, time)
                    queueH.get()
                    log.append(current_job)
                    job_scheduled = True
                    break
            if not job_scheduled:
                schedulingH = False
        time += 1
        
    return log

def priority(job_list):
    nodes_copy = deepcopy(nodes)
    total_jobs = len(job_list)
    log = []
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
                node_index = int(job['node'].replace('node', ''))
                job_completed(node_index, job, nodes_copy)
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
            for node_index in node_groups['A100']:
                node = nodes_copy[node_index]
                if job['gpu_count'] <= node['avail_gpu_count'] and job['cpu_cores'] <= node['avail_cpu_cores'] and job['total_ram_gb'] <= node['avail_ram_gb']:
                    job_started(node_index, job, nodes_copy, time)
                    jobs_removingA.append(job)
                    break

        # Looping through entire queue for H100 to begin jobs that have enough resources (GPU, CPU, RAM)
        for job in queueH.copy():
             for node_index in node_groups['H100']:
                node = nodes_copy[node_index]
                if job['gpu_count'] <= node['avail_gpu_count'] and job['cpu_cores'] <= node['avail_cpu_cores'] and job['total_ram_gb'] <= node['avail_ram_gb']:
                    job_started(node_index, job, nodes_copy, time)
                    jobs_removingH.append(job)
                    break

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
    log_fcfs = fcfs(jobs)
#    queueA, queueH, log_priority = priority(jobs)

    keys_to_display = [
        "job_id",
        "node",
        "gpu_count",
        "cpu_cores",
        "total_ram_gb",
        "submit_time",
        "start_time",
        "end_time",
        "runtime",
        "priority"
    ]


    print("\nList of Jobs:")
    jobs.sort(key=lambda job: (job['gpu_type'], job['submit_time']))
    for job in jobs:
        print(job)

    
    # ===== Check for FCFS =====
    print("\n\n===== FCFS POLICY =====")
    print("\nLog for Node 0 and Node 1:")
    for job in log_fcfs:
        if job['node'] == 'node0' or job['node'] == 'node1': print({key: job[key] for key in keys_to_display})

    print("\nLog for Node 2 and Node 3:")
    for job in log_fcfs:
        if job['node'] == 'node2' or job['node'] == 'node3': print({key: job[key] for key in keys_to_display})


    print("\n\n\n")

    """ # ===== Checks For Priority =====
    print("===== PRIORITY POLICY =====")
    print("\nLog for Node 0 and Node 1:")
    for job in log_priority:
        if job['node'] == 'node0' or job['node'] == 'node1': print({key: job[key] for key in keys_to_display})

    print("\nLog for Node 2 and Node 3:")
    for job in log_priority:
        if job['node'] == 'node2' or job['node'] == 'node3': print({key: job[key] for key in keys_to_display}) """
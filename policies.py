from nodes import nodes
from job_generator import generate_job

def splitting(jobs):
    # all_nodes[0] -> node-01, all_nodes[1] -> node-02 ...
    all_nodes = [[], [], [], []]

    for job in jobs:
        if job['gpu_type'] == 'A100':
            i = 0 if job['gpu_count'] <= 4 else 1
        elif job['gpu_type'] == 'H100':
            i = 2 if job['gpu_count'] <= 4 else 3
        all_nodes[i].append(job)
    
    return all_nodes

    
def fcfs(job_list):
    jobs = splitting(job_list)

    for i, node_jobs in enumerate(jobs):
        jobs[i] = sorted(node_jobs, key=lambda job: job['submit_time'])
    return jobs

    


if __name__ == "__main__":
    jobs = generate_job(20, 42)
    jobs = fcfs(jobs)
    for i in range(0, 4):
        for job in jobs[i]:
            print(f"{job}")
        print()
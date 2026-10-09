import random

def generate_job(n_jobs, seed):
    random.seed(seed)
    jobs = []

    for i in range(1, n_jobs+1):
        job_id = (f"J{i:003d}")
        submit_time = random.randint(0, 100)
        gpu_type = random.choice(['A100', 'H100'])
        gpu_count = random.randint(1, 8)
        cpu_cores = random.choice([1, 2, 4, 8, 16, 32])
        ram_gb_per_cpu = random.choice([1, 2, 4])
        runtime = random.randint(5, 30)
        priority = random.randrange(10, 60, 10)

        jobs.append(
            {
                "job_id": job_id,
                "submit_time": submit_time,
                "gpu_type": gpu_type,
                "gpu_count": gpu_count,
                "cpu_cores": cpu_cores,
                "ram_gb_per_cpu": ram_gb_per_cpu,
                "runtime": runtime,
                "priority": priority
            }
        )

    return jobs


if __name__ == "__main__":
    jobs = generate_job(10, 42)

    for job in jobs:
        print(job)
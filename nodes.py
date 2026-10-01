nodes = [
    {
        "node_id": "node-01",
        "gpu_type": "A100",

        # Total Resources
        "gpu_count": 8,
        "cpu_cores": 128,
        "ram_gb": 1024,

        # Available Resources
        "avail_gpu_count": 8,
        "avail_cpu_cores": 128,
        "avail_ram_gb": 1024

        # Requirements: 1 <= gpu_count <= 4
    },
    {
        "node_id": "node-02",
        "gpu_type": "A100",

        # Total Resources
        "gpu_count": 16,
        "cpu_cores": 256,
        "ram_gb": 2048,

        # Available Resources
        "avail_gpu_count": 16,
        "avail_cpu_cores": 256,
        "avail_ram_gb": 2048

        # Requirement: 5 <= gpu_count <= 8
    },
    {
        "node_id": "node-03",
        "gpu_type": "H100",

        # Total Resources
        "gpu_count": 8,
        "cpu_cores": 128,
        "ram_gb": 1024,

        # Available Resources
        "avail_gpu_count": 8,
        "avail_cpu_cores": 128,
        "avail_ram_gb": 1024

        # Requirements: 1 <= gpu_count <= 4
    },
    {
        "node_id": "node-04",
        "gpu_type": "H100",

        # Total Resources
        "gpu_count": 16,
        "cpu_cores": 256,
        "ram_gb": 2048,

        # Available Resources
        "avail_gpu_count": 16,
        "avail_cpu_cores": 256,
        "avail_ram_gb": 2048

        # Requirements: 5 <= gpu_count <= 8
    }
]


if __name__ == "__main__":
    print(nodes[0]['node_id'])
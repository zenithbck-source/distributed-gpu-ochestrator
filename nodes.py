nodes = [
    {
        "node_id": "node-0",
        "gpu_type": "A100",

        # Total Resources
        "gpu_count": 8,
        "cpu_cores": 32,
        "ram_gb": 64,

        # Available Resources
        "avail_gpu_count": 8,
        "avail_cpu_cores": 32,
        "avail_ram_gb": 64
    },
    {
        "node_id": "node-1",
        "gpu_type": "A100",

        # Total Resources
        "gpu_count": 16,
        "cpu_cores": 64,
        "ram_gb": 128,

        # Available Resources
        "avail_gpu_count": 16,
        "avail_cpu_cores": 64,
        "avail_ram_gb": 128
    },
    {
        "node_id": "node-2",
        "gpu_type": "H100",

        # Total Resources
        "gpu_count": 8,
        "cpu_cores": 32,
        "ram_gb": 64,

        # Available Resources
        "avail_gpu_count": 8,
        "avail_cpu_cores": 32,
        "avail_ram_gb": 64
    },
    {
        "node_id": "node-3",
        "gpu_type": "H100",

        # Total Resources
        "gpu_count": 16,
        "cpu_cores": 64,
        "ram_gb": 128,

        # Available Resources
        "avail_gpu_count": 16,
        "avail_cpu_cores": 64,
        "avail_ram_gb": 128
    }
]


if __name__ == "__main__":
    for node in nodes:
        print(node)
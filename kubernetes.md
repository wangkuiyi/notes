Kubernetes concepts: https://kubernetes.io/docs/concepts

Master components: https://kubernetes.io/docs/concepts/overview/components/#master-components

- kube-apiserver: RESTful API server, horizontally scalable.
- etcd
- kube-scheduler: watch newly created pods that have no node assigned and assign a node.
- kube-controller-manager: runs controllers that are compiled into a single binary on the master.
- cloud-controller-manager: separate cloud-provider-specific code out into another binary.

Node components: https://kubernetes.io/docs/concepts/overview/components/#node-components

- kubelet: run on each node, takes PodSpecs, and makes sure that containers are running and healthy
- kube-proxy: service abstration and connection forwarding.
- container runtime: Docker or others.


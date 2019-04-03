Kubernetes concepts: https://kubernetes.io/docs/concepts

Master components: https://kubernetes.io/docs/concepts/overview/components/#master-components

- kube-apiserver: RESTful API server, horizontally scalable.
- etcd
- kube-scheduler: watch newly created pods that have no node assigned and assign a node.
- kube-controller-manager: runs controllers that are compiled into a single binary on the master.
- cloud-controller-manager: separate cloud-provider-specific code out into another binary.

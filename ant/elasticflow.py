class UserDefinedModule(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)
        self._linear = nn.Linear(1, 1)

    def forward(self, x):
        return self._linear(x)

    def loss(self, x, y):
        return nn.MSELoss()(self.forward(x), y)

    def optimizer(self):
        return torch.optim.SGD(self.parameters(), lr=0.1)

elasticflow.Run(UserDefinedModule,
    runner.K8S("apiserver.k8s.alipay.com", inputs="/oss/yi/house_price*"))

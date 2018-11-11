params = torch.nn.Linear(10, 1)

for iter in range(100):
    x, y = get_batch()

    params.zero_grad()
    loss = F.smooth_l1_loss(fc(x), y)
    loss.backward()

    for param in params.parameters():
        param.data.add_(-0.1 * param.grad.data)

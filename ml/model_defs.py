"""Model definitions shared by training and export."""
from torch import nn


class LSTMClassifier(nn.Module):
    def __init__(self, n_features, hidden=64, layers=1, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, num_layers=layers, batch_first=True,
                            dropout=dropout if layers > 1 else 0.0)
        self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, x):                  # x: (batch, 10, n_features)
        out, _ = self.lstm(x)
        return self.head(out[:, -1]).squeeze(-1)   # logit

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


class TemporalBlock(nn.Module):
    """Two causal dilated convolutions with a residual connection (Bai et al., 2018)."""
    def __init__(self, c_in, c_out, kernel, dilation, dropout):
        super().__init__()
        pad = (kernel - 1) * dilation
        self.conv1 = nn.Conv1d(c_in, c_out, kernel, padding=pad, dilation=dilation)
        self.conv2 = nn.Conv1d(c_out, c_out, kernel, padding=pad, dilation=dilation)
        self.drop, self.relu = nn.Dropout(dropout), nn.ReLU()
        self.down = nn.Conv1d(c_in, c_out, 1) if c_in != c_out else nn.Identity()

    def forward(self, x):                  # x: (batch, channels, time)
        t = x.shape[-1]
        h = self.drop(self.relu(self.conv1(x)[..., :t]))   # crop the right side -> causal
        h = self.drop(self.relu(self.conv2(h)[..., :t]))
        return self.relu(h + self.down(x))


class TCNClassifier(nn.Module):
    """3 levels, dilations 1/2/4, kernel 3: receptive field 29 bins >= the 10-bin window."""
    def __init__(self, n_features, channels=32, levels=3, kernel=3, dropout=0.2):
        super().__init__()
        blocks, c_in = [], n_features
        for i in range(levels):
            blocks.append(TemporalBlock(c_in, channels, kernel, 2 ** i, dropout))
            c_in = channels
        self.net = nn.Sequential(*blocks)
        self.head = nn.Linear(channels, 1)

    def forward(self, x):                  # x: (batch, 10, n_features)
        h = self.net(x.transpose(1, 2))
        return self.head(h[:, :, -1]).squeeze(-1)  # logit


def build_model(kind, n_features, size, layers):
    """kind: 'lstm' (size = hidden units, layers = LSTM layers) or 'tcn' (size = channels, layers = levels)."""
    if kind == "lstm":
        return LSTMClassifier(n_features, hidden=size, layers=layers)
    if kind == "tcn":
        return TCNClassifier(n_features, channels=size, levels=layers)
    raise ValueError(kind)

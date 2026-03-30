# Ruv FANN - API & Command Reference

## Installation

| Method | Command |
|--------|---------|
| npx | `npx ruvnet/ruv-FANN` |
| npm | `npm install ruvnet/ruv-FANN` |

Requires native build tools (C compiler, make).

## Network Types

| Type | Constructor | Description |
|------|-------------|-------------|
| Standard | `new fann.FANN(layers)` | Feedforward fully connected |
| Shortcut | `new fann.ShortcutFANN(layers)` | Direct connections between non-adjacent layers |
| Cascade | `new fann.CascadeFANN(layers)` | Self-growing cascade correlation network |

`layers` is an array of integers: `[inputs, hidden1, ..., hiddenN, outputs]`

## Core API Methods

### Network Lifecycle

| Method | Signature | Description |
|--------|-----------|-------------|
| Create | `new fann.FANN([2, 3, 1])` | Create network with layer sizes |
| Load | `fann.load(filePath)` | Load network from file |
| Save | `net.save(filePath)` | Save network to file |
| Destroy | `net.destroy()` | Free native memory |

### Training

| Method | Signature | Description |
|--------|-----------|-------------|
| Train (file) | `net.trainOnFile(path, opts)` | Train from FANN data file |
| Train (data) | `net.train(data, opts)` | Train from JS arrays |
| Cascade train | `net.cascadeTrain(path, opts)` | Cascade correlation training |

**Training options**:
- `maxEpochs` (number): Maximum training epochs
- `desiredError` (float): Target MSE to stop training
- `epochsBetweenReports` (number): Report interval

**Cascade options**:
- `maxNeurons` (number): Maximum neurons to add
- `desiredError` (float): Target MSE

### Inference

| Method | Signature | Description |
|--------|-----------|-------------|
| Run | `net.run(inputs)` | Run inference on input array |
| Test | `net.test(data)` | Test on data, return MSE |

### Configuration

| Method | Signature | Values |
|--------|-----------|--------|
| Set algorithm | `net.setTrainingAlgorithm(alg)` | `TRAIN_RPROP`, `TRAIN_BATCH`, `TRAIN_QUICKPROP`, `TRAIN_INCREMENTAL` |
| Hidden activation | `net.setActivationFunctionHidden(fn)` | `SIGMOID`, `SIGMOID_SYMMETRIC`, `GAUSSIAN`, `LINEAR`, `ELLIOT` |
| Output activation | `net.setActivationFunctionOutput(fn)` | `SIGMOID`, `SIGMOID_SYMMETRIC`, `LINEAR`, `THRESHOLD` |
| Learning rate | `net.setLearningRate(rate)` | 0.0 - 1.0 (default: 0.7) |
| Momentum | `net.setLearningMomentum(val)` | 0.0 - 1.0 (default: 0.0) |

### Metrics

| Method | Signature | Description |
|--------|-----------|-------------|
| MSE | `net.getMSE()` | Get mean squared error |
| Bit fail | `net.getBitFail()` | Get number of failing output bits |

## Training Data File Format

```
num_patterns num_inputs num_outputs
input1 input2 ... inputN
output1 output2 ... outputM
input1 input2 ... inputN
output1 output2 ... outputM
```

Example (XOR with 4 patterns, 2 inputs, 1 output):
```
4 2 1
0 0
0
0 1
1
1 0
1
1 1
0
```

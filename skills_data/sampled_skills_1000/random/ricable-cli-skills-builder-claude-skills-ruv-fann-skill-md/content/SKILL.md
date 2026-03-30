---
name: "Ruv FANN"
description: "Fast Artificial Neural Network Library - FANN bindings for Node.js with network creation, training, and inference. Use when building neural networks with FANN, training models with backpropagation, running inference on trained networks, or integrating native FANN into Node.js pipelines."
---

# Ruv FANN

Fast Artificial Neural Network Library (FANN) bindings for Node.js providing native-speed network creation, training with backpropagation, and inference for feedforward, cascade, and shortcut neural networks.

## Quick Command Reference

| Task | Command / API |
|------|---------------|
| Install | `npx ruvnet/ruv-FANN` |
| Create network | `fann.create(layers)` |
| Train on data | `fann.train(dataFile, options)` |
| Run inference | `fann.run(inputs)` |
| Save model | `fann.save(filePath)` |
| Load model | `fann.load(filePath)` |
| Get MSE | `fann.getMSE()` |

## Installation

**From GitHub**:
```bash
npx ruvnet/ruv-FANN
```

**As dependency**:
```bash
npx ruvnet/ruv-FANN
```

Requires native build tools (C compiler, make) for FANN library compilation.

## Core API

### Creating Networks

```javascript
const fann = require('ruv-fann');

// Standard feedforward network: 2 inputs, 3 hidden, 1 output
const net = new fann.FANN([2, 3, 1]);

// Shortcut network (direct connections skip layers)
const shortcutNet = new fann.ShortcutFANN([2, 4, 1]);

// Cascade network (starts minimal, grows during training)
const cascadeNet = new fann.CascadeFANN([2, 1]);
```

### Training

```javascript
// Train from file (FANN data format)
net.trainOnFile('xor.data', {
  maxEpochs: 5000,
  desiredError: 0.001,
  epochsBetweenReports: 100
});

// Train from data arrays
const trainingData = [
  { input: [0, 0], output: [0] },
  { input: [0, 1], output: [1] },
  { input: [1, 0], output: [1] },
  { input: [1, 1], output: [0] }
];
net.train(trainingData, {
  maxEpochs: 5000,
  desiredError: 0.001
});

// Cascade training (network grows automatically)
cascadeNet.cascadeTrain('data.train', {
  maxNeurons: 30,
  desiredError: 0.001
});
```

### Inference

```javascript
// Run inference
const output = net.run([1, 0]);
console.log(output); // [0.98] (close to 1 for XOR)

// Batch inference
const results = inputs.map(input => net.run(input));
```

### Save and Load

```javascript
// Save trained network
net.save('trained-model.fann');

// Load previously trained network
const loadedNet = fann.load('trained-model.fann');
const output = loadedNet.run([1, 0]);
```

### Configuration

```javascript
// Set training algorithm
net.setTrainingAlgorithm('TRAIN_RPROP');   // RPROP (default)
net.setTrainingAlgorithm('TRAIN_BATCH');    // Batch
net.setTrainingAlgorithm('TRAIN_QUICKPROP');// Quickprop
net.setTrainingAlgorithm('TRAIN_INCREMENTAL'); // Incremental

// Set activation function
net.setActivationFunctionHidden('SIGMOID_SYMMETRIC');
net.setActivationFunctionOutput('SIGMOID');

// Learning parameters
net.setLearningRate(0.7);
net.setLearningMomentum(0.1);

// Get error metrics
const mse = net.getMSE();
const bitFail = net.getBitFail();
```

## Training Data Format

FANN uses a simple text format for training data:

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

Line 1: `num_patterns num_inputs num_outputs`
Then alternating lines of inputs and expected outputs.

## Common Patterns

### XOR Network (Hello World)
```javascript
const fann = require('ruv-fann');
const net = new fann.FANN([2, 3, 1]);
net.trainOnFile('xor.data', {
  maxEpochs: 5000,
  desiredError: 0.001,
  epochsBetweenReports: 500
});
console.log('XOR(1,0) =', net.run([1, 0]));
net.save('xor-model.fann');
```

### Classification Pipeline
```javascript
const fann = require('ruv-fann');

// Create network matching input/output dimensions
const net = new fann.FANN([featureCount, 64, 32, numClasses]);
net.setTrainingAlgorithm('TRAIN_RPROP');
net.setActivationFunctionHidden('SIGMOID_SYMMETRIC');

// Train
net.train(trainingData, { maxEpochs: 10000, desiredError: 0.01 });

// Evaluate
const predictions = testData.map(sample => {
  const output = net.run(sample.input);
  return output.indexOf(Math.max(...output));
});
```

### Load and Serve
```javascript
const fann = require('ruv-fann');
const net = fann.load('production-model.fann');

// Serve predictions
function predict(features) {
  return net.run(features);
}
```

## Key Options

| Option | Values | Description |
|--------|--------|-------------|
| Training algorithm | `TRAIN_RPROP`, `TRAIN_BATCH`, `TRAIN_QUICKPROP`, `TRAIN_INCREMENTAL` | Backpropagation variant |
| Activation (hidden) | `SIGMOID`, `SIGMOID_SYMMETRIC`, `GAUSSIAN`, `LINEAR`, `ELLIOT` | Hidden layer activation |
| Activation (output) | `SIGMOID`, `SIGMOID_SYMMETRIC`, `LINEAR`, `THRESHOLD` | Output layer activation |
| Learning rate | `0.0 - 1.0` | Step size for weight updates |
| Learning momentum | `0.0 - 1.0` | Momentum for gradient descent |

## RAN DDD Context
**Bounded Context**: Scientific

## References
- **Command reference**: See [references/commands.md](references/commands.md)
- [GitHub](https://github.com/ruvnet/ruv-FANN)

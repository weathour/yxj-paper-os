---
title: Cross-modal Markdown fixture
---

# Methods

As shown in [Fig. 1](#fig-1), the pipeline has two stages.

![System overview with two processing stages.](figure-1.svg){#fig-1}

The objective is defined in Eq. (1).

$$
L(\theta) = \sum_i (y_i - f_\theta(x_i))^2 \tag{1}\label{eq-1}
$$

Algorithm 1 applies the update rule.

Algorithm 1: Training procedure. {#alg-1}

```algorithm
Input: observations X
Output: fitted parameters theta
Initialize theta
for each observation in X:
    update theta
return theta
```

# Results

Table 1 reports the two evaluated methods.

Table 1: Main comparison. {#table-1}

| Method | Score | Runtime |
|---|---:|---:|
| Baseline | 0.71 | 12.0 |
| Proposed | 0.79 | 10.5 |

The advantage in Fig. 1 is discussed together with Table 1.

# References

Fig. 99, Table 99, Eq. (99), and Algorithm 99 are reference-list noise.

```text
Fig. 98 and Table 98 are code-block noise.
```

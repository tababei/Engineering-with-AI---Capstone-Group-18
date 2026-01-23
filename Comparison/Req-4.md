# Validation of the Should requirement
> Should critically analyze and demonstrate what features were learned (human step detection, etc.) by the TLIO model

For this experiment we determined a straight line to be the course. The course is once taken on foot, the model's prediction being saved in [view-walking.png](./view-walking.png). Once more, the course is taken but this time on a wheelchair that is pushed from behind and this time the results are saved in [view-rolling.png](./view-rolling.png). The contrast is stark and obvious when comparing the two images. The absence of perturbations on the Y-axis in the rolling results clearly shows that "steps", spikes in vertical displacement (dy) graph, are associated with forward movement by the model. 

**Visual Comparison:**

| **Walking Results** | **Rolling (Wheelchair) Results** |
|:---:|:---:|
| ![Walking](./view-walking.png) | ![Rolling](./view-rolling.png) |
| *Note the spikes in vertical displacement (dy) indicating steps.* | *Note the relatively smooth Y-axis; the model fails to detect forward movement.* |

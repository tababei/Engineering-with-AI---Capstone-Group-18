# Results commentary
Alongside the shell files that contain the code that gets the results, we have also uploaded some of the results themselves under the generic name "view-ID-NE.png". The ID represents a certain dataset to enable ease of identification and N represents the number of epochs of the trained model. 

## Comparison
Looking at "view-1008221029329889-10E.png" and at "view-1008221029329889-100E.png" the starkest comparison is in the RMSE and RPE. Both have a lower error by about 10%. This "diminishing returns" effect is expected due to our limited data which can make up for our limited dataset with an ever increasing amount of Epochs. The trajectory seems to be closer to the Ground Truth, confirming our expectations. 

There are some instances in which we observe a higher RMSE and RPE, looking at 353903485150701 or . The motion is quite simplistic, with not a lot of twists and turns, and still the errors seem to increase. In other cases, the RMSE remains relatively constant across runs, the RPE decreasing quite a bit (case of 955615084638299). The model seems to perform better on intricate and noisy data when it is trained for longer, and worse on simpler data. 

# Validating completion of the first "Must"
The results seen in this folder confirms the completion of the first "Must". They align with our approach in the Project Plan as they closely resemble the findings illustrated in the paper. 

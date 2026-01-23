# Engineering with AI - Capstone Group 18
This is a repository containing the process, code that we have used, and results we have obtained for our Capstone project in the Engineering with AI minor.

We have used the Delft Blue supercomputer to help facilitate rapid training, testing of the model, as well as running the Extended Kalman Filter (EKF) and generating the final plots. The base code used in our project is located at [TLIO](https://github.com/CathIAS/TLIO). The main idea of that paper was to study the improvements of an AI used in combination with a more traditional approach to GNSS-restricted localization. 

In order to use the code our approach closely follows this line of thinking: create a suitable environment on a Linux OS machine (Delft Blue in our case), train the algorithm, test the algorithm, run it with EKF and get the resulting plots. The data the paper uses is not in their original repository and must be downloaded from a separate [Google Drive](https://drive.google.com/file/d/10Bc6R-s0ZLy9OEK_1mfpmtDg3jIu8X6g/view). 

## 1. Preliminary requirements
To begin with, we upload the TLIO repository to our dedicated storage in the supercomputer via OnDemand. After it is done uploading we navigate to "TLIO/src" and create a new directory named "local_data" which will serve as the location of the data from the Drive. Note that it will take some time and may fail during the upload of all the data. 
> **Note:** Uploading numerous large files may fail.
In case of failure, stop the upload (as all subsequent uploads will begin failing) and take note of the last uploaded folder. Click on the "Help" button above and select "Restart Web Server". On the next upload attempt, selection starts from that last deleted folder. Note that this may take numerous attempts. Once all the data has been uploaded we can move onto the next step.

## 2. Environment creation - "sbatch tlio_env.sh"
The code needs an environment to run on, containing all the neccesary packages and versions of Python, PyTorch, Numpy, etc.. We have automated this process to just running our `tlio_env.sh` file. To queue this file you must be in the "TLIO" directory and type `sbatch tlio_env.sh` or `srun tlio_env.sh` if you wish to run it in your local terminal on the supercomputer. This command applies to all our files and can be summarized as this: `sbatch YOUR_FILE.sh`. 

## 3. Training the model - "sbatch train_conda_final.sh"
The model must be trained on some type of data in order for it to learn how to correctly predict the movement. `sbatch train_conda_final.sh` is the command that will queue the training of the model. We have trained two models, one with 10 Epochs, and the other with 100 Epochs. A 10% improvement has been noticed with the tenfold increase in training time. The training lasted around 15 minutes for 10 Epochs and around 2 hours and 30 minutes for 100 Epochs. 

## 4. Testing the model - "sbatch test_conda_final.sh"
This command queues the testing of the model on unseen data and outputs a gross summary per each dataset. The duration of this process is around 15-20 minutes. 

## 5. EKF and plotting the results - "sbatch run_ekf.sh" then "sbatch run_plots.sh"
This first command makes use of the CSV raw outputs and the NPY files to see if the predictions of the model by itself and together with the filter. After the `run_ekf.sh` finishes we are only left with trajectory, therefore we need to also run the "run_plots.sh" file to get the outputs of all that data (acceleration bias and error, displacement, trajectory in 2D and 3D, rotation error, etc.). 

## Notes on GitHub directories
To separate our findings clearly we have a "Results" directory which is host to the outputs of our model, further separated into "Training_Results", "Test_Results", "EKF_Results", "Custom_Results". Each of these will have a small Markdown file explaining its contents. 

The "Synthetic_Data" directory contains the files and results that prove the second and third Must requirements have been completed. 

The "Comparison" directory contains proof of completion for the Should requirement.

The "Robustness" directory contains the results of experimental data tests on the model, completing the first Could requirement. 

## Further notes on using the model on custom data 
Inside the [Google Drive](https://drive.google.com/file/d/10Bc6R-s0ZLy9OEK_1mfpmtDg3jIu8X6g/view) data folder there are a series of text files named "all_ids.txt", "test_list.txt", "train_list.txt", "val_list.txt". In order to run custom data, these files must be edited as such:

1) Open the desired file with any text editor
2) At the top insert a new line which contains the name of the custom directory (i.e. "custom_walking")
3) In OnDemand create a new directory with the same name as before ("custom_walking")
4) Inside this new directory add the four corresponding files (see "Custom_data_example")
5) The next time you run the model this new data will be used

**There are some limitations in how short the data can be. If this is the case an error will be raised in the output logs.**

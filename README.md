# Engineering-with-AI---Capstone-Group-18
This is a repository containing the process, code that we have used, and results we have obtained for our Capstone project in the Engineering with AI minor.

We have used the Delft Blue supercomputer to help facilitate rapid training, testing of the model, as well as running the Extended Karman Filter (EKF) and generating the final plots. The base code used in our project is located at https://github.com/CathIAS/TLIO. The main idea of that paper was to study the improvements of an AI used in combination with a more traditional approach to GNSS-restricted localization. 

In order to use the code our approach closely follows this line of thinking: create a suitable environment on a Linux OS machine (Delft Blue in our case), train the algorithm, test the algorithm, run it with EKF and get the resulting plots. The data the paper uses is not in their original repository and must be downloaded from a separate Google Drive (https://drive.google.com/file/d/10Bc6R-s0ZLy9OEK_1mfpmtDg3jIu8X6g/view). 

# 1. Preliminary requirements
To begin with, we upload the TLIO repository to our dedicated storage in the supercomputer via OnDemand. After it is done uploading we navigate to "TLIO/src" and create a new directory/folder named "local_data" which will serve as the location of the data from the Drive. Note that it will take some time and may fail during the upload of all the data. In case of failure, stop the upload (as all subsequent uploads will begin failing) and take note of the last uploaded folder. Click on the "Help" button above and select "Restart Web Server". On the next upload attempt, selection starts from that last deleted folder. Note that this may take numerous attempts. Once all the data has been uploaded we can move onto the next step.

# 2. Environment creation

#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=TLIO_EKF
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=5200M
#SBATCH --output=slurm_ekf-%j.out

# --- SETUP ---
module purge
module load slurm
module load miniconda3
source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# --- STEP 1: CONVERT MODEL ---
echo "[Step 1] Converting model to TorchScript..."
srun python src/convert_model_to_torchscript.py \
    --model_path models/resnet/checkpoint_best.pt \
    --model_param_path models/resnet/parameters.json \
    --out_dir models/resnet/

# --- STEP 2: RUN EKF ---
echo "[Step 2] Running Extended Kalman Filter..."

srun python src/main_filter.py \
    --root_dir src/local_data/golden-new-format-cc-by-nc-with-imus \
    --model_path models/resnet/model_torchscript.pt \
    --model_param_path models/resnet/parameters.json \
    --out_dir ekf_outputs \
    --erase_old_log \
    --save_as_npy \
    --initialize_with_offline_calib

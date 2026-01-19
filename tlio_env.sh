#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=install_tlio
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-task=1
#SBATCH --mem=5300M
#SBATCH --output=install_log.out

# --- 1. SETUP ---
module purge
module load slurm
module load miniconda3

source $(conda info --base)/etc/profile.d/conda.sh

conda env remove -n tlio -y || true

# --- 2. PHASE 1: CREATE ENV (With PIP explicitly added) ---
# Added 'pip' to the list so the command exists.
echo "[Phase 1] Creating Environment..."
conda create -n tlio python=3.9 pip pytorch=1.13.1 torchvision=0.14.1 pytorch-cuda=11.7 -c pytorch -c nvidia -y

# --- 3. PHASE 2: THE NUMPY FIX ---
conda activate tlio

echo "[Phase 2] Overwriting Numpy..."
# Using 'python -m pip' guarantees we use the pip belonging to this python
python -m pip install numpy==1.23.5 scipy pandas matplotlib tqdm h5py evo termcolor

# --- 4. VERIFY ---
echo "--- Done ---"
python -c "import numpy; print(f'Numpy: {numpy.__version__}')"

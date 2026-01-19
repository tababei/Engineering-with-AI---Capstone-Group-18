#!/bin/bash
# ==============================================================================
# MASTER SCRIPT: TLIO FINAL 
# ==============================================================================

# --- 1. SETUP & MODULES ---
echo "[1/4] Loading Environment..."
module purge
module load slurm
module load miniconda3

source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio

# --- 2. ENFORCE DEPENDENCIES (Strict Order: Torch -> NumPy) ---
echo "[2/4] Verifying Versions..."

# STEP A: Check GPU Torch (FIRST)
cuda_check=$(python -c "import torch; print(torch.cuda.is_available())")
if [ "$cuda_check" == "False" ]; then
    echo "    -> [Fixing GPU] Re-installing PyTorch 1.11+cu113..."
    pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
else
    echo "    -> [GPU Status] PyTorch is GPU-ready."
fi

# STEP B: Check NumPy 1.23.5 (LAST - to fix the crash)
current_numpy=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null)
if [ "$current_numpy" != "1.23.5" ]; then
    echo "    -> [Fixing Crash] Downgrading Numpy from $current_numpy to 1.23.5..."
    pip install "numpy==1.23.5" --force-reinstall
else
    echo "    -> [Numpy Status] Correct version (1.23.5) verified."
fi

# --- 3. GENERATE SUBMISSION SCRIPT ---
echo "[3/4] Generating sbatch script..."

cat << 'EOF' > train_conda_final.sh
#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=TLIO_Final
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=5200MB
#SBATCH --account=education-ae-bsc-lr
#SBATCH --output=slurm-%j.out

# --- A. Environment ---
module purge
module load slurm
module load miniconda3
source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio

# --- B. Runtime Fixes ---
# GLIBCXX Fix: Point to Conda's modern libraries
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# --- C. Debugging ---
echo "Node: $(hostname)"
echo "Numpy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "CUDA: $(python -c 'import torch; print(torch.cuda.is_available())')"

# --- D. Execution ---
echo "Starting Training..."
# python -u for unbuffered output
srun python -u src/main_net.py \
    --mode train \
    --root_dir src/local_data/golden-new-format-cc-by-nc-with-imus \
    --out_dir models/resnet \
    --epochs 10 \
    --dataset_style ram \
    --workers 4 \
    --no-persistent_workers
EOF

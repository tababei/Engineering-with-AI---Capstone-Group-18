#!/bin/bash
# ==============================================================================
# MASTER SCRIPT: TLIO TESTING
# ==============================================================================

# --- 1. SETUP ---
module purge
module load slurm
module load miniconda3
source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio

# --- 2. GENERATE SLURM SCRIPT ---
cat << 'EOF' > test_conda_final.sh
#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=TLIO_Test
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=5200MB
#SBATCH --account=education-ae-bsc-lr
#SBATCH --output=slurm_test-%j.out

# --- A. Environment ---
module purge
module load slurm
module load miniconda3
source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio

# --- B. Runtime Fixes ---
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# --- C. Execution ---
echo "Starting Inference..."
echo "Model: models/resnet/checkpoint_best.pt"

srun python -u src/main_net.py \
    --mode test \
    --root_dir src/local_data/golden-new-format-cc-by-nc-with-imus \
    --model_path models/resnet/checkpoint_best.pt \
    --out_dir test_outputs_resnet \
    --dataset_style ram \
    --workers 4 \
    --no-persistent_workers
EOF

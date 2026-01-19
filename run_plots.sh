#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=TLIO_PLOT
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-task=0
#SBATCH --mem-per-cpu=5200M
#SBATCH --output=slurm_plot-%j.out

# --- 1. SETUP ---
module purge
module load slurm
module load miniconda3
source $(conda info --base)/etc/profile.d/conda.sh
conda activate tlio

# --- 2. VERIFICATION ---
# Check if folders actually exist in the current directory (TLIO root)
if [ ! -d "ekf_outputs" ]; then
    echo "ERROR: 'ekf_outputs' folder not found in $(pwd)"
    exit 1
fi

if [ ! -d "test_outputs_resnet" ]; then
    echo "ERROR: 'test_outputs_resnet' folder not found in $(pwd)"
    exit 1
fi

# --- 3. PREPARE WORKSPACE ---
echo "Setting up workspace..."
rm -rf plotting_workspace  # Clean start
mkdir -p plotting_workspace/filter/tlio_resnet
mkdir -p plotting_workspace/net/tlio_resnet

# We link the folders from the ROOT directory (TLIO/), not src/
# We use absolute paths to be safe.

echo "Linking EKF results..."
ln -sf $(readlink -f ekf_outputs)/* plotting_workspace/filter/tlio_resnet/

echo "Linking Network results..."
ln -sf $(readlink -f test_outputs_resnet)/* plotting_workspace/net/tlio_resnet/

# --- 4. RUN PLOTTING ---
echo "Generating plots..."
cd src

# Run the plot batch script
# Note: We use '../plotting_workspace' because we just cd'd into src
python -m batch_runner.plot_batch \
    --root_dir local_data/golden-new-format-cc-by-nc-with-imus \
    --runname_globbing "tlio_resnet" \
    --filter_dir ../plotting_workspace/filter \
    --ronin_dir ../plotting_workspace/net

echo "Done. Results are in plotting_workspace/filter/tlio_resnet/"

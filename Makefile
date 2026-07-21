.PHONY: install install-cpu clean shell

install:
	@echo "Installing base dependencies with Poetry..."
	poetry install
	@echo "Installing mmcv-full and mmdet directly via pip (bypassing mim)..."
	poetry run pip install mmcv-full==1.7.2 -f https://download.openmmlab.com/mmcv/dist/cu113/torch1.11.0/index.html
	poetry run pip install mmdet==2.28.2
	@echo "Forcing NumPy downgrade to fix any pip overrides..."
	poetry run pip install "numpy<2.0.0"

install-cpu:
	@echo "Installing base environment..."
	poetry install
	@echo "Overriding PyTorch with CPU-only wheels..."
	poetry run pip install torch==1.11.0+cpu torchvision==0.12.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
	@echo "Installing mmcv-full and mmdet..."
	poetry run pip install mmcv-full==1.7.2 -f https://download.openmmlab.com/mmcv/dist/cpu/torch1.11.0/index.html
	poetry run pip install mmdet==2.28.2
	@echo "Forcing NumPy downgrade to fix any pip overrides..."
	poetry run pip install "numpy<2.0.0"

clean:
	@echo "Wiping the Poetry virtual environment..."
	poetry env remove --all

shell:
	poetry shell

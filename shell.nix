{ pkgs ? import <nixpkgs> {
#  overlays = [(import (builtins.fetchTarball {url = https://github.com/nix-community/neovim-nightly-overlay/archive/master.tar.gz;}))];
}
}:
with pkgs;
let
  my-python-packages = python-packages: with python-packages; [
    ptpython
    pip
    # other python packages you want
  ];
  python-with-my-packages = python3.withPackages my-python-packages;

in
  mkShell {
    buildInputs = [
    # Customized packages
    python-with-my-packages
    jq
  ];

  shellHook = ''
    export PIP_PREFIX="$(pwd)/_build/pip_packages"
    export PYTHONPATH="$(pwd)/_build/pip_packages/lib/python3.10/site-packages:$(pwd)/_build/pip_packages/local/lib/python3.10/dist-packages:$PYTHONPATH"
    export PATH="$(pwd)/_build/pip_packages/bin:$PATH"
    # PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
  '';
}

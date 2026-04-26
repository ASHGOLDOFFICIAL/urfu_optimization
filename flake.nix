{
  description = "DevShell for lp_solver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { nixpkgs, ... }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell rec {
      buildInputs = with pkgs; ([
        python3
        python3Packages.pip
        python3Packages.venvShellHook
        stdenv.cc.cc.lib
        zlib
      ]);
      
      env = {
        LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${builtins.toString (pkgs.lib.makeLibraryPath buildInputs)}";
        RUST_SRC_PATH = "${pkgs.rustPlatform.rustLibSrc}";
      };
      
      venvDir = ".venv";
  
      postVenvCreation = ''
        pip install -r requirements.txt
      '';
    };
  };
} 
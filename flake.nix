{
  description = "A PCParadise bot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix-src.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix-src }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ poetry2nix-src.overlay ];
        };
        packageInfo = {
          projectDir = ./.;
        };
      in {
        defaultPackage = pkgs.poetry2nix.mkPoetryApplication packageInfo;
        devShell = (pkgs.poetry2nix.mkPoetryEnv packageInfo);
      });
}

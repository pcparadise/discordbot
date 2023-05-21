{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.alejandra.url = "github:kamadorueda/alejandra/3.0.0";
  inputs.alejandra.inputs.nixpkgs.follows = "nixpkgs";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    alejandra,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      discordbot = pkgs.stdenv.mkDerivation {
        name = "discordbot";
        buildInputs = [pkgs.poetry];
        src = ./.;
        buildPhase = ''
          mkdir -p $out/bin
          mkdir -p $out/lib
          cp -R $src/* $out/lib
          echo "#!${pkgs.bash}/bin/bash
          ${pkgs.poetry}/bin/poetry -C $out/lib install
          ${pkgs.poetry}/bin/poetry -C $out/lib run run
          " > $out/bin/discordbot
          chmod 555 $out/bin/discordbot
        '';
      };
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = [pkgs.gcc pkgs.pkg-config pkgs.pyright];
        buildInputs = [pkgs.poetry];
      };

      # TODO: might be better to use poetry2nix here
      packages.discordbot = discordbot;
      defaultPackage = self.packages.${system}.discordbot;
      formatter = alejandra.defaultPackage.${system};
    });
}

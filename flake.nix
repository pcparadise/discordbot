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
    flake-utils.lib.eachDefaultSystem (system: let pkgs = import nixpkgs { inherit system; }; in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = [ pkgs.gcc pkgs.pkg-config ];
        buildInputs = [ pkgs.poetry ];
      };
      formatter = alejandra.defaultPackage.${system};
    });
}

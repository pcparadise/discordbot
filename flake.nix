{
  description = "A PCParadise bot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix-src.url = "github:nix-community/poetry2nix";
    config-ini.url = "path:config.ini";
    config-ini.flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix-src, config-ini }:
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
        defaultPackage = pkgs.poetry2nix.mkPoetryApplication (packageInfo // { 
          src = ./.; 
          postInstall = ''
            mkdir $out/PCParadiseBot
            ln -s ${config-ini} $out/PCParadiseBot/config.ini
            wrapProgram $out/bin/run --set XDG_CONFIG_HOME $out
          '';
        });
        devShell = (pkgs.poetry2nix.mkPoetryEnv packageInfo);
      });
}
